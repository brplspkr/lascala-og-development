"""Original La Scala 1977 reference reconstruction; see provenance.json."""
import sys, os, math, json
sys.path.append('/Applications/FreeCAD.app/Contents/Resources/lib')
import FreeCAD as App, Part, Sketcher
from itertools import combinations
OUT=os.path.dirname(os.path.abspath(__file__))
I=25.4
W,D,H,T=23.75*I,24.5*I,35.25*I,.75*I
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
doc=App.newDocument('LaScala_OG_1977_R1_Reference')
panels=doc.addObject('App::DocumentObjectGroup','CabinetPanels');panels.Label='01 - Cabinet panels (editable sketches and pads)'
ref=doc.addObject('App::DocumentObjectGroup','DriverReferences');ref.Label='02 - Horns / driver envelopes - approximate reference only'
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
left=panel('LeftSide','08L - Left full-height side',[loop_rect(0,0,D,H-T)],T,(-W/2,0,0),YZ,source='Cut list 08: 24-1/2 x 34-1/2 inches')
right=panel('RightSide','08R - Right full-height side',[loop_rect(0,0,D,H-T)],T,(W/2-T,0,0),YZ,source='Cut list 08: 24-1/2 x 34-1/2 inches')
panel('Top','10 - Cabinet top',[loop_rect(-W/2,0,W/2,D)],T,(0,0,H-T),source='Cut list 10: 23-3/4 x 24-1/2 inches')
panel('BassBack','01 - Bass-bin back',[loop_rect(-IW/2,0,IW/2,SHELF)],T,(0,D,0),XZ,source='Cut list 01: 22-1/4 wide x 23-3/4 high inches')
panel('BassShelf','06 - Bass-bin top / upper shelf',[loop_rect(-IW/2,0,IW/2,D-T)],T,(0,0,Z1),source='Cut list 06: 22-1/4 x 23-3/4 inches')
# Source cut-list 07 opening, oriented with truncated tip toward front.
a,b=15.125*I/2,7*I/2
rear=(D-T)-4.3125*I
shoulder=rear-4.6875*I
tip=shoulder-6.5*I
aperture=[(-a,rear),(-a,shoulder),(-b,tip),(b,tip),(a,shoulder),(a,rear)]
frame=panel('AccessFrame','07 - Bottom access frame',[loop_rect(-IW/2,0,IW/2,D-T),list(reversed(aperture))],T,source='07 pentagonal access opening from dimensioned drawing; hatch mounting/rebate unresolved')
# Flush closure is deliberately a separate provisional body; not a claimed factory panel 11.
cx,cy=0,sum(y for x,y in aperture)/len(aperture)
plug=[(x*.997,cy+(y-cy)*.997) for x,y in aperture]
panel('AccessClosure','R1 - Provisional flush access closure',[plug],T,status='PROVISIONAL - closure for reference model only',source='Factory part 11 is listed as 23 x 23-1/2 inches; its overlay/rebate arrangement is not resolved. This fitted plug is NOT that factory part.',color=(.50,.31,.15))
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
    panel('Nose'+side,'05'+side[0]+' - Doghouse angled nose panel',[roof],Z1-Z0,(0,0,Z0),status='DERIVED - section fitted; bevel/blank requires checking',source='Front tip, 16-3/4 outer width, motorboard and side positions from assembled section. Source lists 16-3/8 roof blank and 60-degree detail; those do not fully reconcile with section. Do not fabricate from R1.')
# Four rear flare wings: air passage expands from throat height 13 to full 22-1/4.
# Model their air-contact faces from the assembled throat and wall dimensions.
ZC=(Z0+Z1)/2
rise=(Z1-Z0-13*I)/2
slope=rise/DOG_HALF
normal_z=T*math.sqrt(1+slope*slope)
for s,side in [(1,'Right'),(-1,'Left')]:
    for upper,which in [(True,'Upper'),(False,'Lower')]:
        q=[0,DOG_HALF]
        if upper:
            f0=ZC+6.5*I; cross=max(0,(Z1-normal_z-f0)/slope)
            poly=[(0,f0),(s*DOG_HALF,Z1),(s*cross,Z1),(0,f0+normal_z)]
        else:
            f0=ZC-6.5*I;cross=max(0,(f0-normal_z-Z0)/slope)
            poly=[(0,f0),(s*DOG_HALF,Z0),(s*cross,Z0),(0,f0-normal_z)]
        panel(which+side+'Wing','02 - '+which+' '+side.lower()+' throat flare wing',[poly],3*I,(0,D-T,0),XZ,status='DERIVED - air-contact profile; blank/bevel requires checking',source='Four wings across 3-inch rear plenum; 13 to 22-1/4 inch vertical expansion. Cut list wing blank 9-1/8 x 3; source bevel notes 30 / 60 degrees. R1 uses fitted section surfaces.')
# Vertical triangular splitter on inside rear wall, centered over the 13-inch throat.
split=[(-1.125*I,D-T),(1.125*I,D-T),(0,D-T-1.125*I)]
panel('RearSplitter','03 - Rear vertical splitter',[split],13*I,(0,0,ZC-6.5*I),source='13 high; 2-1/4 wide; approximately 1-1/8 projection from source 90-degree splitter sketch')
# Upper motorboard holes from cut-list page 2.
baffle_z=SHELF;baffle_h=10.75*I
mid_w,mid_h=16.1875*I,5.625*I
mid_bot=baffle_z+1.59375*I
mid=loop_rect(-mid_w/2,mid_bot,mid_w/2,mid_bot+mid_h)
tw_w,tw_h=4.15625*I,.5625*I
tw_bot=baffle_z+baffle_h-1.65625*I
tw=loop_rect(-tw_w/2,tw_bot,tw_w/2,tw_bot+tw_h)
panel('UpperMotorboard','09 - Upper motorboard, midrange and tweeter cutouts',[loop_rect(-IW/2,baffle_z,IW/2,H-T),list(reversed(mid)),list(reversed(tw))],T,(0,T,0),XZ,source='22-1/4 x 10-3/4 inch board. Mid opening 16-3/16 x 5-5/8; tweeter 4-5/32 x 9/16. Interpreted small tweeter vertical dimension; verify against hardware.')

# Approximate removable driver reference shapes, explicitly excluded from cabinet STEP.
def reference(name,label,shape,note):
    o=doc.addObject('Part::Feature',name);o.Label=label;o.Shape=shape;ref.addObject(o)
    o.addProperty('App::PropertyString','Evidence','Reference');o.Evidence='APPROXIMATE VISUAL / CLEARANCE REFERENCE ONLY'
    o.addProperty('App::PropertyString','DrawingNote','Reference');o.DrawingNote=note
    if o.ViewObject:o.ViewObject.ShapeColor=black
    refs.append(o);return o

def rect_wire_y(y,w,h,zc):
    pts=[V(-w/2,y,zc-h/2),V(w/2,y,zc-h/2),V(w/2,y,zc+h/2),V(-w/2,y,zc+h/2)]
    return Part.makePolygon(pts+[pts[0]])
def horn(name,label,w,h,zc,depth,throat):
    outer=Part.makeLoft([rect_wire_y(T,w+12,h+12,zc),rect_wire_y(depth,throat+6,throat+6,zc)],True,False)
    inner=Part.makeLoft([rect_wire_y(T-.5,w,h,zc),rect_wire_y(depth+.5,throat,throat,zc)],True,False)
    shell=outer.cut(inner)
    reference(name,label,shell,'Straight loft placeholder, NOT an acoustic horn design or a hardware manufacturing model. Exact K-400/K-77 contours and driver depth unverified.')
    return shell
horn('MidHornReference','REFERENCE - K-400-style mid horn silhouette',mid_w,mid_h,mid_bot+mid_h/2,440,18)
horn('TweeterHornReference','REFERENCE - K-77-style tweeter silhouette',tw_w,tw_h,tw_bot+tw_h/2,65,12)
# Woofer envelope points into the closed doghouse; cone faces rear throat.
woofer=Part.makeCone(178,80,105,V(0,MB_FRONT,ZC),V(0,-1,0)).fuse(Part.makeCylinder(78,45,V(0,MB_FRONT-105,ZC),V(0,-1,0)))
reference('WooferReference','REFERENCE - 15-inch woofer clearance envelope',woofer,'Generic 15-inch driver envelope. Bolt pattern, basket and exact K-33 model not verified.')
# Parameters and provenance survive STEP via exported names and FCStd via table/properties.
sheet=doc.addObject('Spreadsheet::Sheet','Dimensions');sheet.Label='00 - Dimensions and verification status'
rows=[['Parameter','mm','Reference'],['Width',W,'1977 drawing: 23-3/4 in'],['Depth',D,'1977 drawing: 24-1/2 in'],['Height',H,'1977 drawing: 35-1/4 in; brochure says 35-1/2'],['Nominal stock',T,'3/4 inch, not 18 mm'],['Bass interior height',Z1-Z0,'22-1/4 in'],['Bass throat width',3*I,'3 in'],['Bass throat height',13*I,'13 in'],['Status','REFERENCE MODEL','NOT APPROVED FOR FABRICATION'],['Unresolved','Bevels / closure','See provenance.json']]
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
report={'units':'mm','version':'R1 reference reconstruction','cabinet_parts':len(parts),'reference_parts':len(refs),'bounds_mm':[bounds.XLength,bounds.YLength,bounds.ZLength],'solids':checks,'positive_volume_panel_overlaps':overlaps,'manufacturing_release':False}
with open(os.path.join(OUT,'validation.json'),'w') as f:json.dump(report,f,indent=2)
if overlaps:raise RuntimeError('Panel intersections: '+str(overlaps))
if any(not c['valid'] or c['solids']!=1 for c in checks):raise RuntimeError('Invalid / multi-solid part')
Part.export(parts,os.path.join(OUT,'LaScala_OG_1977_R1_Cabinet.step'))
Part.export(parts+refs,os.path.join(OUT,'LaScala_OG_1977_R1_With_Reference_Drivers.step'))
doc.saveAs(os.path.join(OUT,'LaScala_OG_1977_R1.FCStd'))
# Portable meshes for preview, exported from the verified solids.
meshes=[]
for p in parts+refs:
    vs,fs=p.Shape.tessellate(1.0)
    meshes.append({'name':p.Name,'label':p.Label,'reference':p in refs,'vertices':[[v.x,v.y,v.z] for v in vs],'faces':fs})
with open(os.path.join(OUT,'preview_meshes.json'),'w') as f:json.dump(meshes,f)
provenance={'basis':'1977 Factory LaScala Dimensions, two-page scan posted in Klipsch community; community copy, authenticity not independently certified','source_page':'https://community.klipsch.com/topic/179112-la-scala-lf-build/','reference_images':['../References/1977-LaScala-assembly.jpg','../References/1977-LaScala-cut-list.jpg'],'manufacturer_brochure':'../References/original-klipsch-brochure.pdf','height_choice':'1977 drawing 35-1/4 in used consistently; later brochure 35-1/2 in is not silently mixed into geometry','coordinate_system':'mm; X centered across width, Y increases from front to rear, Z up; floor at Z=0','manufacturing_release':False,'uncertainties':['Doghouse roof blank length/bevel notes do not fully reconcile with assembled section dimensions. R1 uses section geometry with continuous constant-thickness walls and fitted miters.','Four rear wing air-contact surfaces derived from 3-inch rear plenum and 13 to 22-1/4 inch expansion. Source wing blank / bevel geometry requires confirmation.','Factory bottom panel 11 overlay/rebate arrangement unresolved. R1 includes an explicitly provisional flush pentagonal plug so the model is closed.','Tweeter vertical offset read from low-resolution drawing; exact fastener holes, rebates, gaskets and joinery not modeled.','All driver and horn shapes are approximate reference envelopes; lofts are not validated acoustic contours. No crossover, wiring or fasteners modeled.','Nominal 3/4-inch plywood modeled as 19.05 mm; measure actual stock before production.'],'parts':manifest}
with open(os.path.join(OUT,'provenance.json'),'w') as f:json.dump(provenance,f,indent=2)
print(json.dumps({'output':OUT,'parts':len(parts),'valid':True,'overlaps':overlaps,'bounds_mm':report['bounds_mm']}))
