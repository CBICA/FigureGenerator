# Screenshot Maker

This project helps create screenshots for medical images for use in presentations and/or manuscripts.

## Inputs

- Image (single or multiple co-registered)
  - for multiple images:
    - perform sanity check using logic in https://github.com/CBICA/GaNDLF/blob/master/GANDLF/utils.py#L610
- Mask: Optional
- Mask opacity: Optional (default is 100 - full opacity)
- Slice number: Optional
  - if not defined and mask is present, binarize the mask and use the slices with largest area
  - if not defined and mask is absent, use middle of each axis from image(s)

## Outputs

### For single image

- Single PNG containing all axes views in x-axis
- First row only image
- Second row image and mask overlayed based on opacity

### For multiple images

Two images:
1. Stack previous in in multiple rows (2-column manuscript)
2. Stack previous in in multiple columns (1-column manuscript)
