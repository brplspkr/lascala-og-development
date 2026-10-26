import bpy, math, json, os
from mathutils import Vector
OUT=os.path.dirname(os.path.abspath(__file__))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=48
scene.cycles.use_denoising=True
scene.render.resolution_x=1500;scene.render.resolution_y=1750;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.world.color=(.25,.25,.25)
scene.view_settings.view_transform='AgX'
wood=bpy.data.materials.new('Warm unfinished birch plywood');wood.use_nodes=True
n=wood.node_tree.nodes;l=wood.node_tree.links
p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=.53
tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=5.5;tex.inputs['Detail'].default_value=2
coords=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(3,40,2)
l.new(coords.outputs['Generated'],mapping.inputs[0]);l.new(mapping.outputs[0],tex.inputs['Vector'])
ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.2;ramp.color_ramp.elements[0].color=(.38,.23,.10,1);ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(.69,.49,.26,1)
l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
black=bpy.data.materials.new('Horn reference matte charcoal');black.diffuse_color=(.025,.029,.032,1);black.use_nodes=True;black.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.022,.026,.029,1);black.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.65
objs={}
for part in json.load(open(os.path.join(OUT,'preview_meshes.json'))):
    mesh=bpy.data.meshes.new(part['name']);mesh.from_pydata([[x/1000 for x in v] for v in part['vertices']],[],part['faces']);mesh.update()
    obj=bpy.data.objects.new(part['name'],mesh);scene.collection.objects.link(obj);obj.data.materials.append(black if part['reference'] else wood);objs[part['name']]=obj
    # Fine edge highlights; physical geometry is unchanged in the CAD files.
    bevel=obj.modifiers.new('Preview edge light','BEVEL');bevel.width=.00045;bevel.segments=2
    bevel.limit_method='ANGLE'
    obj.modifiers.new('Preview normals','WEIGHTED_NORMAL')
mat=bpy.data.materials.new('Studio floor');mat.diffuse_color=(.17,.19,.20,1)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.02005));bpy.context.object.data.materials.append(mat)

def area(name,loc,power,size):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,.25,.4))-ob.location).to_track_quat('-Z','Y').to_euler()
area('Key',(-1.8,-2.4,2.6),420,2.4);area('Fill',(2,-.8,1.3),220,1.8);area('Rim',(0,2,2.7),500,2)
cam=bpy.data.cameras.new('Camera');camera=bpy.data.objects.new('Camera',cam);scene.collection.objects.link(camera);scene.camera=camera;cam.type='ORTHO';cam.ortho_scale=1.32
camera.location=(1.3,-1.9,1.33);target=Vector((0,.25,.44));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
scene.render.filepath=os.path.join(OUT,'LaScala_OG_R2_assembled.png');bpy.ops.render.render(write_still=True)
for name in ['RightSide','Top','BassShelf']:objs[name].hide_render=True
camera.location=(1.5,-1.5,1.7);camera.rotation_euler=(Vector((0,.27,.42))-camera.location).to_track_quat('-Z','Y').to_euler();cam.ortho_scale=1.35
scene.render.filepath=os.path.join(OUT,'LaScala_OG_R2_cutaway.png');bpy.ops.render.render(write_still=True)
# Return the saved scene to assembled state.
for name in ['RightSide','Top','BassShelf']:objs[name].hide_render=False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'LaScala_OG_R2_Preview.blend'))
