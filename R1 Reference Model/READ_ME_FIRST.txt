ORIGINAL LA SCALA - 1977 REFERENCE RECONSTRUCTION - R1

This is a complete-cabinet CAD reference model, not a manufacturing release.

FILES
LaScala_OG_1977_R1.FCStd: 18 separate cabinet bodies, each with an editable outline sketch and pad; 3 removable approximate driver/horn references; dimension table.
LaScala_OG_1977_R1_Cabinet.step: cabinet panels only, 18 solid parts.
LaScala_OG_1977_R1_With_Reference_Drivers.step: cabinet plus approximate visual/clearance references.
LaScala_OG_R1_assembled.png and LaScala_OG_R1_cutaway.png: previews from the exported solid geometry.
build_model.py: regenerates CAD with the installed FreeCAD Python runtime.
provenance.json: source links, interpretation notes and uncertainty for each part.
validation.json: solid validity, dimensions and panel-interference checks.

DIMENSIONS
Width 603.25 mm (23-3/4 inches)
Depth 622.30 mm (24-1/2 inches)
Height 895.35 mm (35-1/4 inches)
Nominal plywood 19.05 mm (3/4 inch)
The 1977 drawing height is used consistently. The separately saved later manufacturer brochure lists 35-1/2 inches; that is not silently mixed into this reconstruction.

CONSTRUCTION BASIS
Two images titled "1977 Factory LaScala Dimensions", posted in the Klipsch community thread "La Scala LF build":
https://community.klipsch.com/topic/179112-la-scala-lf-build/
These are community-posted copies; factory authenticity is not independently certified.
The two source images are saved in the References folder alongside this version folder.
The available German metric drawing uses 16 mm material and different overall dimensions; it was NOT substituted for the 3/4-inch 1977 design.

VERIFY BEFORE CUTTING
1. Angled doghouse panel blank lengths and end bevels: this reconstruction fits the assembled section, while the source's blank/bevel detail requires confirmation.
2. Four rear throat-flare wings: air-contact surfaces are derived from throat and plenum dimensions; exact blanks/miters need confirmation.
3. Factory bottom panel 11 is listed separately. Its overlay/rebate arrangement is unresolved. The assembled R1 uses an explicitly provisional flush pentagonal closure; it is not claimed to reproduce factory part 11.
4. Upper motorboard tweeter offset was interpreted from a low-resolution drawing. Confirm it and all mounting dimensions against actual horns.
5. Horn lofts and woofer shape are approximate visual/clearance envelopes. They are not acoustic horn profiles or accurate driver manufacturing models.
6. Fasteners, gaskets, crossover, wiring, joinery details and production tolerances are not included. Measure actual plywood thickness.

VALIDATION
18 separate cabinet solids are valid and have no positive-volume overlaps.
The cabinet STEP was reimported successfully as 18 valid solids with the expected overall dimensions.
The native CAD file was reopened successfully with 18 bodies and 18 sketches.
These geometry checks do not establish acoustic performance or fabrication readiness.
