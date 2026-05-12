---
title: Adding a Building Element
description: How to add a new building element to the Commonbuild library.
---

Each building element is defined as a YAML file in `src/content/elements/`.
Here is how to add one.

## 1. Create a new YAML file

Create a file in `src/content/elements/` using a descriptive slug, for example `wall-clt-200.yaml`.

## 2. Fill in the required fields

```yaml
name: CLT Wall 200mm
ifc_class: IfcWall
description: >
  Cross-laminated timber wall panel used as a structural and
  insulating element in mass timber construction.
total_thickness_mm: 200
u_value: 0.30
fire_rating: REI 60
tags:
  - exterior
  - timber
  - clt
  - structural
layers:
  - position: 1
    name: Exterior cladding
    material: Larch boards
    thickness_mm: 25
    function: finish
  - position: 2
    name: CLT panel
    material: Cross-laminated timber 5-ply
    thickness_mm: 160
    function: structural
  - position: 3
    name: Interior finish
    material: Gypsum board
    thickness_mm: 12.5
    function: finish
```

## Required fields

| Field | Type | Description |
|---|---|---|
| `name` | string | Display name of the element |
| `ifc_class` | string | IFC class (e.g. `IfcWall`, `IfcSlab`, `IfcRoof`) |
| `description` | string | Short description of the assembly |
| `total_thickness_mm` | number | Overall thickness in millimetres |
| `u_value` | number | Thermal transmittance in W/m²K |
| `fire_rating` | string | Fire resistance classification |
| `tags` | list | Searchable tags (element type, material, use case) |
| `layers` | list | Ordered list of layers (see below) |

## Layer fields

Each item in `layers` requires:

| Field | Type | Description |
|---|---|---|
| `position` | number | Order from exterior (1) to interior |
| `name` | string | Layer name |
| `material` | string | Material specification |
| `thickness_mm` | number | Thickness in mm (use `0` for membranes or services) |
| `function` | string | One of: `finish`, `insulation`, `structural`, `moisture control`, `waterproofing`, `protection`, `services` |

## 3. Commit and push

Once your file is saved, commit it to the repository. The site rebuilds automatically via GitHub Actions.
