#!/usr/bin/env python3
"""Generate IFC4 files from YAML building element definitions.

Each YAML element becomes one .ifc file in public/ifc/.
Every layer is a separate IfcExtrudedAreaSolid with a surface style
colour derived from its function type, stacked along the thickness axis.
The element also carries an IfcMaterialLayerSet with full layer data.
"""

import sys
from pathlib import Path

import yaml
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.guid

# ---------------------------------------------------------------------------
# Colour map: function keyword → RGB (0-1 range)
# ---------------------------------------------------------------------------
FN_COLORS: dict[str, tuple[float, float, float]] = {
    "finish":      (0.29, 0.87, 0.50),
    "insulation":  (0.98, 0.75, 0.14),
    "structural":  (0.38, 0.65, 0.98),
    "moisture":    (0.65, 0.54, 0.98),
    "vapour":      (0.65, 0.54, 0.98),
    "waterproof":  (0.13, 0.83, 0.93),
    "protection":  (0.96, 0.45, 0.71),
    "services":    (0.58, 0.64, 0.72),
}
DEFAULT_COLOR = (0.58, 0.64, 0.72)


def fn_color(function: str) -> tuple[float, float, float]:
    fn = function.lower()
    for key, color in FN_COLORS.items():
        if key in fn:
            return color
    return DEFAULT_COLOR


# ---------------------------------------------------------------------------
# IFC geometry helpers
# ---------------------------------------------------------------------------

def make_surface_style(
    model: ifcopenshell.file,
    rgb: tuple[float, float, float],
    name: str = "",
) -> "ifcopenshell.entity_instance":
    r, g, b = rgb
    colour = model.createIfcColourRgb(None, r, g, b)
    shading = model.createIfcSurfaceStyleShading(colour, 0.0)
    return model.createIfcSurfaceStyle(name or None, "BOTH", (shading,))


def make_layer_solid(
    model: ifcopenshell.file,
    thickness_mm: float,
    element_length_mm: float,
    element_height_mm: float,
    offset_x_mm: float,
    surface_style: "ifcopenshell.entity_instance",
) -> "ifcopenshell.entity_instance":
    """
    Create one IfcExtrudedAreaSolid box for a single layer.

    Coordinate convention (for walls):
      X axis  = thickness direction (layers stack along X)
      Y axis  = element length
      Z axis  = element height (vertical)

    The box occupies:
      X: [offset_x, offset_x + thickness]
      Y: [0, element_length]
      Z: [0, element_height]
    """
    # 2-D profile centred at (length/2, height/2) so it spans [0..length] x [0..height]
    profile = model.createIfcRectangleProfileDef(
        "AREA",
        None,
        model.createIfcAxis2Placement2D(
            model.createIfcCartesianPoint((element_length_mm / 2.0, element_height_mm / 2.0)),
            None,
        ),
        element_length_mm,
        element_height_mm,
    )

    # 3-D placement: origin at (offset_x, 0, 0)
    # Axis  (local Z = extrusion direction) → world X
    # RefDir (local X = profile X-axis)     → world Y
    placement = model.createIfcAxis2Placement3D(
        model.createIfcCartesianPoint((offset_x_mm, 0.0, 0.0)),
        model.createIfcDirection((1.0, 0.0, 0.0)),
        model.createIfcDirection((0.0, 1.0, 0.0)),
    )

    solid = model.createIfcExtrudedAreaSolid(
        profile,
        placement,
        model.createIfcDirection((0.0, 0.0, 1.0)),  # extrude along local Z = world X
        thickness_mm,
    )

    # Attach colour
    model.createIfcStyledItem(solid, (surface_style,), None)

    return solid


# ---------------------------------------------------------------------------
# Main generator
# ---------------------------------------------------------------------------

def generate_ifc(yaml_path: Path, output_path: Path) -> None:
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    model: ifcopenshell.file = ifcopenshell.api.run("project.create_file", version="IFC4")

    # Project
    project = ifcopenshell.api.run(
        "root.create_entity", model, ifc_class="IfcProject", name=data["name"]
    )

    # Units: millimetres
    ifcopenshell.api.run("unit.assign_unit", model)

    # Geometric contexts
    model_ctx = ifcopenshell.api.run("context.add_context", model, context_type="Model")
    body_ctx = ifcopenshell.api.run(
        "context.add_context",
        model,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=model_ctx,
    )

    # Spatial hierarchy
    site = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcSite", name="Site")
    building = ifcopenshell.api.run(
        "root.create_entity", model, ifc_class="IfcBuilding", name="Building"
    )
    storey = ifcopenshell.api.run(
        "root.create_entity", model, ifc_class="IfcBuildingStorey", name="Ground Floor"
    )
    ifcopenshell.api.run("aggregate.assign_object", model, products=[site], relating_object=project)
    ifcopenshell.api.run(
        "aggregate.assign_object", model, products=[building], relating_object=site
    )
    ifcopenshell.api.run(
        "aggregate.assign_object", model, products=[storey], relating_object=building
    )

    # Building element
    ifc_class = data.get("ifc_class", "IfcBuildingElementProxy")
    element = ifcopenshell.api.run(
        "root.create_entity", model, ifc_class=ifc_class, name=data["name"]
    )
    ifcopenshell.api.run(
        "spatial.assign_container", model, products=[element], relating_structure=storey
    )

    # Element placement at world origin
    ifcopenshell.api.run(
        "geometry.edit_object_placement",
        model,
        product=element,
    )

    # IfcMaterialLayerSet
    mat_set = ifcopenshell.api.run(
        "material.add_material_set",
        model,
        name=data["name"],
        set_type="IfcMaterialLayerSet",
    )

    for layer_data in data.get("layers", []):
        mat = ifcopenshell.api.run(
            "material.add_material", model, name=layer_data["material"]
        )
        ifc_layer = ifcopenshell.api.run(
            "material.add_layer", model, layer_set=mat_set, material=mat
        )
        ifc_layer.LayerThickness = layer_data.get("thickness_mm", 0)
        ifc_layer.Name = layer_data.get("name", "")

    # Assign IfcMaterialLayerSetUsage to element
    category = data.get("category", "walls")
    layer_set_direction = "AXIS2" if category == "walls" else "AXIS3"

    usage = model.createIfcMaterialLayerSetUsage(
        mat_set,
        layer_set_direction,
        "POSITIVE",
        0.0,
    )
    model.createIfcRelAssociatesMaterial(
        ifcopenshell.guid.new(),
        None, None, None,
        (element,),
        usage,
    )

    # Geometry: stack one solid box per layer
    layers = data.get("layers", [])
    MIN_DISPLAY_MM = 2.0  # minimum thickness for very thin layers (membranes etc.)

    if category == "walls":
        el_length_mm = 3000.0
        el_height_mm = 2500.0
    else:
        el_length_mm = 3000.0
        el_height_mm = 3000.0

    solids = []
    offset = 0.0

    for layer_data in layers:
        raw_thickness = layer_data.get("thickness_mm") or 0
        display_thickness = max(MIN_DISPLAY_MM, float(raw_thickness))
        color = fn_color(layer_data.get("function", ""))
        style = make_surface_style(model, color, layer_data.get("name", ""))
        solid = make_layer_solid(
            model, display_thickness, el_length_mm, el_height_mm, offset, style
        )
        solids.append(solid)
        offset += display_thickness

    shape_rep = model.createIfcShapeRepresentation(
        body_ctx, "Body", "SweptSolid", solids
    )
    element.Representation = model.createIfcProductDefinitionShape(
        None, None, (shape_rep,)
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    model.write(str(output_path))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def load_database(repo_root: Path):
    """Laad de drie YAML-databestanden en join ze tot een lijst van element-dicts
    die compatibel zijn met de generate_ifc functie."""
    data_dir = repo_root / "src" / "data"

    with open(data_dir / "elements.yaml") as f:
        elements = yaml.safe_load(f) or []
    with open(data_dir / "layers.yaml") as f:
        all_layers = yaml.safe_load(f) or []
    with open(data_dir / "materials.yaml") as f:
        all_materials = yaml.safe_load(f) or []

    mat_by_id = {m["id"]: m for m in all_materials}

    # Groepeer lagen per element_id en verrijk met materiaalnaam
    layers_by_element: dict[str, list] = {}
    for layer in all_layers:
        eid = layer["element_id"]
        mat = mat_by_id.get(layer.get("material_id", ""), {})
        layers_by_element.setdefault(eid, []).append({
            "position":     layer.get("position", 0),
            "name":         layer.get("name", ""),
            # material-veld = ifc_material_name uit DB, anders product-naam, anders material_id
            "material":     mat.get("ifc_material_name") or mat.get("name") or layer.get("material_id", ""),
            "thickness_mm": layer.get("thickness_mm", 0),
            "function":     layer.get("function", ""),
        })

    # Sorteer lagen op positie
    for eid in layers_by_element:
        layers_by_element[eid].sort(key=lambda l: l["position"])

    # Combineer tot generate_ifc-compatibele dicts
    return [
        {**el, "layers": layers_by_element.get(el["id"], [])}
        for el in elements
    ]


def main() -> None:
    repo_root = Path(__file__).parent.parent
    ifc_dir = repo_root / "public" / "ifc"

    elements = load_database(repo_root)

    if not elements:
        print("No elements found in src/data/elements.yaml.")
        sys.exit(1)

    print(f"Generating IFC files for {len(elements)} element(s)…")
    errors = 0

    for element_data in elements:
        stem = element_data["id"]
        out = ifc_dir / f"{stem}.ifc"

        # Schrijf tijdelijk naar een temp-dict die generate_ifc verwacht
        import tempfile, json
        tmp = Path(tempfile.mktemp(suffix=".yaml"))
        try:
            with open(tmp, "w") as f:
                yaml.dump(element_data, f, allow_unicode=True)
            generate_ifc(tmp, out)
            print(f"  ✓  {out.relative_to(repo_root)}")
        except Exception as exc:
            print(f"  ✗  {stem}: {exc}")
            import traceback; traceback.print_exc()
            errors += 1
        finally:
            tmp.unlink(missing_ok=True)

    if errors:
        sys.exit(1)
    print("Done.")


if __name__ == "__main__":
    main()
