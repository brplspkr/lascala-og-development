"""Original La Scala 1977 reference reconstruction; see provenance.json."""
import sys, os, math, json
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, Part, Sketcher
from itertools import combinations
OUT=os.path.dirname(os.path.abspath(__file__))
I=25.4
W,D,H,T=23.75*I,24.5*I,23.75*I,.75*I
IW=W-2*T
Z0=T; Z1=23*I; SHELF=23.75*I
MB_REAR=D-T-3*I; MB_FRONT=MB_REAR-T
DOG_HALF=7.625*I; DOG_OUT=DOG_HALF+T
CORNER=MB_REAR-7.5*I
V=App.Vector
XY=App.Rotation()
XZ=App.Rotation(V(1,0,0),90) # normal toward front (-Y)
YZ=App.Rotation(V(1,1,1),120) # U -> Y, V -> Z, normal -> X
wood=(.64,.43,.23); black=(.045,.047,.05)
doc=App.newDocument('LaScala_OG_LF_Only_R3_Reference')
panels=doc.addObject('App::DocumentObjectGroup','CabinetPanels');panels.Label='01 - Cabinet panels (editable sketches and pads)'
ref=doc.addObject('App::DocumentObjectGroup','DriverReferences');ref.Label='02 - LF woofer clearance reference only'
parts=[]; refs=[]; manifest=[]

def loop_rect(x0,y0,x1,y1):return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]

def panel(name,label,loops,depth,origin=(0,0,0),rotation=XY,status='Dimensioned / derived from 1977 drawing',source='',color=wood):
    body=doc.addObject('PartDesign::Body',name);body.Label=label;panels.addObject(body)
    sk=doc.addObject('Sketcher::SketchObject',name+'_Outline');body.addObject(sk)
    sk.Label='Editable outline - '+label
    sk.Placement=App.Placement(V(*origin),rotation)
    for poly in loops:
        for a,b in zip(poly,poly[1:]+poly[:1]):
            n=sk.addGeometry(Part.LineSegment(V(a[0],a[1],0),V(b[0],b[1],0)),False)
            sk.addConstraint(Sketcher.Constraint('Block',n))
    doc.recompute()
    pad=body.newObject('PartDesign::Pad',name+'_Pad');pad.Label=label+' - thickness';pad.Profile=sk;pad.Length=depth
    sk.Visibility=False
    body.addProperty('App::PropertyString','Evidence','Reference');body.Evidence=status
    body.addProperty('App::PropertyString','DrawingNote','Reference');body.DrawingNote=source
    body.addProperty('App::PropertyLength','NominalStock','Reference');body.NominalStock=T
    doc.recompute()
    if body.ViewObject:
        body.ViewObject.ShapeColor=color;body.ViewObject.LineColor=(.12,.08,.04)
    parts.append(body);manifest.append({'name':name,'label':label,'evidence':status,'note':source})
    if body.Shape.isNull() or not body.Shape.isValid():raise RuntimeError('Invalid '+name)
    return body

# Shell, all dimensions mm. X is centered; front Y=0; up Z.
left=panel('LeftSide','08L - Left LF-only side',[loop_rect(0,0,D,H)],T,(-W/2,0,0),YZ,status='R3 LF-ONLY ADAPTATION',source='R2 side shortened to 23-3/4 inches high, flush with original bass shelf. Depth and thickness unchanged.')
right=panel('RightSide','08R - Right LF-only side',[loop_rect(0,0,D,H)],T,(W/2-T,0,0),YZ,status='R3 LF-ONLY ADAPTATION',source='R2 side shortened to 23-3/4 inches high, flush with original bass shelf. Depth and thickness unchanged.')
panel('BassBack','01 - Bass-bin back',[loop_rect(-IW/2,0,IW/2,SHELF)],T,(0,D,0),XZ,source='Cut list 01: 22-1/4 wide x 23-3/4 high inches')
panel('BassShelf','06 - Closed flat LF top / horn support deck',[loop_rect(-IW/2,0,IW/2,D-T)],T,(0,0,Z1),source='Cut list 06: 22-1/4 x 23-3/4 inches')
# Source cut-list 07 opening, oriented with truncated tip toward front.
a,b=15.125*I/2,7*I/2
rear=(D-T)-4.3125*I
shoulder=rear-4.6875*I
tip=shoulder-6.5*I
aperture=[(-a,rear),(-a,shoulder),(-b,tip),(b,tip),(a,shoulder),(a,rear)]
frame=panel('AccessFrame','07 - Bottom access frame',[loop_rect(-IW/2,0,IW/2,D-T),list(reversed(aperture))],T,source='07 pentagonal access opening from dimensioned drawing; hatch mounting/rebate unresolved')
# Factory part 11 is a separate rectangular underlay, retained as its own solid.
# Retain the user-approved R2 3/4-inch underlaid access cover without change.
# The source specifies 23 x 23-1/2 in but does not locate it precisely in plan.
# Centering under the cabinet is the explicit R2 placement assumption.
bottom_w,bottom_d=23*I,23.5*I
panel('SpeakerBottom','11 - Removable rectangular speaker bottom, 23 x 23-1/2',[loop_rect(-bottom_w/2,(D-bottom_d)/2,bottom_w/2,(D+bottom_d)/2)],T,(0,0,-T),status='UNCHANGED FROM R2 - underlay thickness and centered placement remain assumptions',source='Cut list 11: separate 23 x 23-1/2 inch rectangular cover, screwed to woofer-door frame, not glued. R2-approved 3/4 inch underlaid cover retained, giving 24-1/2 inch complete LF-only height. Exact hole pattern, gasket and offsets unverified.',color=(.50,.31,.15))
# Doghouse motorboard: 15-1/4 wide x 22-1/4 high; 3 x 13 throat.
slot=loop_rect(-1.5*I,(Z0+Z1)/2-6.5*I,1.5*I,(Z0+Z1)/2+6.5*I)
panel('WooferMotorboard','12 - Woofer motorboard / 3 x 13 throat',[loop_rect(-DOG_HALF,Z0,DOG_HALF,Z1),list(reversed(slot))],T,(0,MB_REAR,0),XZ,source='Cut list 12: 15-1/4 x 22-1/4, centered 3 x 13 inch slot')
# Mitered pentagonal doghouse. Section dimensions govern the assembly.
L=math.hypot(DOG_OUT,CORNER); inset_tip=T*L/DOG_OUT
inner_corner_y=(CORNER*DOG_HALF+T*L)/DOG_OUT
for s,side in [(1,'Right'),(-1,'Left')]:
    roof=[(0,0),(s*DOG_OUT,CORNER),(s*DOG_HALF,inner_corner_y),(0,inset_tip)]
    wall=[(s*DOG_OUT,CORNER),(s*DOG_OUT,MB_REAR),(s*DOG_HALF,MB_REAR),(s*DOG_HALF,inner_corner_y)]
    if s<0:roof.reverse();wall.reverse()
    panel('Doghouse'+side,'04'+side[0]+' - Doghouse straight side',[wall],Z1-Z0,(0,0,Z0),source='7-1/2 inch outside straight run, 3/4 stock; front miter derived')
    panel('Nose'+side,'05'+side[0]+' - Doghouse angled nose panel',[roof],Z1-Z0,(0,0,Z0),status='DERIVED - section fitted; bevel/blank requires checking',source='Front tip, 16-3/4 outer width, motorboard and side positions from assembled section. Source lists 16-3/8 roof blank and 60-degree detail; those do not fully reconcile with section. Do not fabricate from R2.')
# Four rear flare wings: air passage expands from throat height 13 to full 22-1/4.
# Model their air-contact faces from the assembled throat and wall dimensions.
ZC=(Z0+Z1)/2
rise=(Z1-Z0-13*I)/2
slope=math.tan(math.radians(30.0))
normal_z=T*math.sqrt(1+slope*slope)
for s,side in [(1,'Right'),(-1,'Left')]:
    for upper,which in [(True,'Upper'),(False,'Lower')]:
        q=[0,DOG_HALF]
        if upper:
            f0=ZC+6.5*I; cross=max(0,(Z1-normal_z-f0)/slope)
            poly=[(0,f0),(s*DOG_HALF,f0+slope*DOG_HALF),(s*DOG_HALF,Z1),(s*cross,Z1),(0,f0+normal_z)]
        else:
            f0=ZC-6.5*I;cross=max(0,(f0-normal_z-Z0)/slope)
            poly=[(0,f0),(s*DOG_HALF,f0-slope*DOG_HALF),(s*DOG_HALF,Z0),(s*cross,Z0),(0,f0-normal_z)]
        panel(which+side+'Wing','02 - '+which+' '+side.lower()+' throat flare wing',[poly],3*I,(0,D-T,0),XZ,status='TRUE 30 DEGREE FACE - source endpoint and exact blank/bevel still require verification',source='Four wings retain the 3-inch rear plenum and slot-edge starts Z=136.525 / 466.725 mm. Face slope is exactly 30 degrees. At X=+/-193.675 mm, air face ends 5.656687 mm from the floor/shelf corner; stock is trimmed against those horizontal planes. No slot/cabinet dimensions moved. Wing blank and joint detail remain unverified.')
# Vertical triangular splitter on inside rear wall, centered over the 13-inch throat.
split=[(-1.125*I,D-T),(1.125*I,D-T),(0,D-T-1.125*I)]
panel('RearSplitter','03 - Rear vertical splitter',[split],13*I,(0,0,ZC-6.5*I),source='13 high; 2-1/4 wide; approximately 1-1/8 projection from source 90-degree splitter sketch')
# Approximate removable driver reference shapes, explicitly excluded from cabinet STEP.
def reference(name,label,shape,note):
    o=doc.addObject('Part::Feature',name);o.Label=label;o.Shape=shape;ref.addObject(o)
    o.addProperty('App::PropertyString','Evidence','Reference');o.Evidence='APPROXIMATE VISUAL / CLEARANCE REFERENCE ONLY'
    o.addProperty('App::PropertyString','DrawingNote','Reference');o.DrawingNote=note
    if o.ViewObject:o.ViewObject.ShapeColor=black
    refs.append(o);return o

# Woofer envelope points into the closed doghouse; cone faces rear throat.
woofer=Part.makeCone(178,80,105,V(0,MB_FRONT,ZC),V(0,-1,0)).fuse(Part.makeCylinder(78,45,V(0,MB_FRONT-105,ZC),V(0,-1,0)))
reference('WooferReference','REFERENCE - 15-inch woofer clearance envelope',woofer,'Generic 15-inch driver envelope. Bolt pattern, basket and exact K-33 model not verified.')
# Parameters and provenance survive STEP via exported names and FCStd via table/properties.
sheet=doc.addObject('Spreadsheet::Sheet','Dimensions');sheet.Label='00 - Dimensions and verification status'
rows=[['Parameter','mm','Reference'],['Width',W,'1977 drawing: 23-3/4 in'],['Depth',D,'1977 drawing: 24-1/2 in'],['LF shell height',H,'23-3/4 inches; top shelf stays at its R2 location'],['Complete LF height',H+T,'24-1/2 inches including R2 underlaid cover'],['Wing face angle',30,'degrees; slot-edge start unchanged'],['Nominal stock',T,'3/4 inch, not 18 mm'],['Bass interior height',Z1-Z0,'22-1/4 in'],['Bass throat width',3*I,'3 in'],['Bass throat height',13*I,'13 in'],['Status','REFERENCE MODEL','NOT APPROVED FOR FABRICATION'],['Unresolved','Wing endpoints / cover offsets','See provenance.json']]
for r,row in enumerate(rows,1):
    for c,value in enumerate(row):sheet.set(chr(65+c)+str(r),str(value))

doc.recompute()
# Solid validity + all-pairs positive-volume interference check.
checks=[]; overlaps=[]
for p in parts+refs:
    checks.append({'part':p.Name,'valid':p.Shape.isValid(),'solids':len(p.Shape.Solids),'volume_mm3':p.Shape.Volume})
for a,b in combinations(parts,2):
    # Bounding-box rejection first, then exact common volume.
    ba,bb=a.Shape.BoundBox,b.Shape.BoundBox
    if min(ba.XMax,bb.XMax)-max(ba.XMin,bb.XMin)<1e-5 or min(ba.YMax,bb.YMax)-max(ba.YMin,bb.YMin)<1e-5 or min(ba.ZMax,bb.ZMax)-max(ba.ZMin,bb.ZMin)<1e-5:continue
    v=a.Shape.common(b.Shape).Volume
    if v>.05:overlaps.append({'a':a.Name,'b':b.Name,'mm3':v})
compound=Part.makeCompound([p.Shape for p in parts]);bounds=compound.BoundBox
report={'units':'mm','version':'R3 LF-only - separate horn on top','cabinet_parts':len(parts),'reference_parts':len(refs),'bounds_mm':[bounds.XLength,bounds.YLength,bounds.ZLength],'solids':checks,'positive_volume_panel_overlaps':overlaps,'manufacturing_release':False}
with open(os.path.join(OUT,'validation.json'),'w') as f:json.dump(report,f,indent=2)
if overlaps:raise RuntimeError('Panel intersections: '+str(overlaps))
if any(not c['valid'] or c['solids']!=1 for c in checks):raise RuntimeError('Invalid / multi-solid part')
# Independent review assertions and comparison with R1 protected solids.
assert abs(bounds.XLength-W)<1e-6 and abs(bounds.YLength-D)<1e-6 and abs(bounds.ZLength-(H+T))<1e-6
assert abs(math.degrees(math.atan(slope))-30)<1e-10
assert abs(doc.getObject('SpeakerBottom').Shape.BoundBox.XLength-23*I)<1e-6
assert abs(doc.getObject('SpeakerBottom').Shape.BoundBox.YLength-23.5*I)<1e-6
r2=App.openDocument(os.path.join(OUT,'..','LaScala_OG_1977_R2.FCStd'))
protected=['BassBack','BassShelf','AccessFrame','SpeakerBottom','WooferMotorboard','DoghouseRight','DoghouseLeft','NoseRight','NoseLeft','RearSplitter','UpperRightWing','LowerRightWing','UpperLeftWing','LowerLeftWing']
comparisons=[]
for name in protected:
    before,after=r2.getObject(name).Shape,doc.getObject(name).Shape
    delta=before.cut(after).Volume+after.cut(before).Volume
    assert delta<.001, (name,delta)
    comparisons.append({'part':name,'symmetric_difference_mm3':delta})
# Each shorter side is exactly its R2 parent clipped at the unchanged bass-deck top.
limit=Part.makeBox(W+2,D+2,H+T+1,V(-W/2-1,-1,-T-1))
for name in ['LeftSide','RightSide']:
    expected=r2.getObject(name).Shape.common(limit)
    actual=doc.getObject(name).Shape
    delta=expected.cut(actual).Volume+actual.cut(expected).Volume
    assert delta<.001,(name,delta)
assert all(doc.getObject(n) is None for n in ['Top','UpperMotorboard','MidHornReference','TweeterHornReference'])
assert len(parts)==16 and len(refs)==1
# The original shelf, rear and shortened side edges all meet in one flat top plane.
assert all(abs(doc.getObject(n).Shape.BoundBox.ZMax-H)<1e-6 for n in ['LeftSide','RightSide','BassShelf','BassBack'])
review={'R2_LF_parts_unchanged':comparisons,'shortened_sides':'Exact R2 side solids clipped at Z=603.25 mm','removed':['original upper cabinet top','upper motorboard','midrange reference','tweeter reference'],'retained_closed_top':'Original bass-bin shelf plus flush side/rear edges; no added top layer and no change in LF chamber height','wing_face_angle_deg':math.degrees(math.atan(slope)),'slot_edges_z_mm':[ZC-6.5*I,ZC+6.5*I],'wing_face_corner_offset_mm':rise-DOG_HALF*slope,'bottom_blank_mm':[bottom_w,bottom_d,T],'shell_height_mm':H,'complete_height_mm':H+T,'crossover_scope':'Passive: original or compatible upgraded network, selected against final drivers','horn_support':'A separate freestanding upper horn assembly may sit on the flat closed LF deck. No unknown horn dimensions, brackets or mounting holes invented.'}
with open(os.path.join(OUT,'review_verification.json'),'w') as f:json.dump(review,f,indent=2)
App.setActiveDocument(doc.Name)
Part.export(parts,os.path.join(OUT,'LaScala_OG_LF_Only_R3_Cabinet.step'))
Part.export(parts+refs,os.path.join(OUT,'LaScala_OG_LF_Only_R3_Full_Assembly.step'))
doc.saveAs(os.path.join(OUT,'LaScala_OG_LF_Only_R3.FCStd'))
# Portable meshes for preview, exported from the verified solids.
meshes=[]
for p in parts+refs:
    vs,fs=p.Shape.tessellate(1.0)
    meshes.append({'name':p.Name,'label':p.Label,'reference':p in refs,'vertices':[[v.x,v.y,v.z] for v in vs],'faces':fs})
with open(os.path.join(OUT,'preview_meshes.json'),'w') as f:json.dump(meshes,f)
provenance={'basis':'LF-only adaptation of the checked R2 original La Scala reference reconstruction','reference_R2':'../LaScala_OG_1977_R2.FCStd','layout_reference':'User photo s-l1600.jpg: LF bin with separate upper horn assembly resting above','source_page':'https://community.klipsch.com/topic/179112-la-scala-lf-build/','coordinate_system':'mm; X centered, Y=0 front, Y=622.3 rear. Original bin underside Z=0; removable cover Z=-19.05 to 0; closed deck top Z=603.25','nominal_complete_dimensions_mm':[W,D,H+T],'manufacturing_release':False,'changes':['Removed upper cabinet, its top cap, upper motorboard and both upper horn references.','Shortened both outer sides to existing bass-shelf top.','Retained existing sealed LF top deck at its exact R2 position; no extra top sheet.'],'unchanged':'All fourteen retained LF panels, including floor/access cover, motorboard, angled doghouse, rear wings, splitter and shelf/back, are geometrically identical to R2. Generic woofer envelope also retained.','crossover_scope':'Passive crossover; exact original/upgrade selection awaits final driver/horn choice. DSP out of scope.','uncertainties':['R2 doghouse roof blank / bevel interpretation remains unverified.','R2 true 30-degree wing faces retained, including 5.656687 mm air-face endpoint offset.','R2 bottom thickness and centered underlay placement retained; exact gasket and screw locations not verified.','Woofer remains a generic clearance envelope. Separate upper horn, its support feet, fasteners, wiring and crossover enclosure are not modeled.','No load capacity or stability rating for a particular horn/stand is implied. Mounting can be detailed once actual horn/stand dimensions are supplied.','Nominal 3/4-inch material is modeled as 19.05 mm.'],'parts':manifest}
with open(os.path.join(OUT,'provenance.json'),'w') as f:json.dump(provenance,f,indent=2)
print(json.dumps({'output':OUT,'parts':len(parts),'valid':True,'overlaps':overlaps,'bounds_mm':report['bounds_mm']}))
