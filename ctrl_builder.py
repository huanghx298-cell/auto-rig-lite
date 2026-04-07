

import math

import maya.cmds as cmds

from rig import rig_runtime


class CtrlFactory:

    CTRL_SIZE_PRESET = {"large": 18.0, "medium": 10.0,
                        "xsmall": 4.0, "small": 2.0, }

    @staticmethod
    def _resolve_radius(size):
        if isinstance(size, (int, float)):
            return float(size)
        try:
            return CtrlFactory.CTRL_SIZE_PRESET[size]
        except KeyError:
            raise RuntimeError(f"Unknown ctrl size tier: {size}")

    @staticmethod
    def create_ctrl_fk(**kwargs):
        args = dict(name="CTRL_FK", size="medium",
                    normal=(0, 1, 0), color_index=18)
        args.update(kwargs)

        radius = CtrlFactory._resolve_radius(args["size"])

        ctrl = cmds.circle(n=args["name"], r=radius,
                           nr=args["normal"], ch=False)[0]

        shapes = cmds.listRelatives(ctrl, s=True, f=True) or []
        for s in shapes:
            cmds.setAttr(s + ".overrideEnabled", 1)
            cmds.setAttr(s + ".overrideColor", int(args["color_index"]))

        return ctrl

    @staticmethod
    def create_ctrl_ik(**kwargs):
        args = dict(name="CTRL_IK", size="medium", color_index=13)
        args.update(kwargs)

        extent = CtrlFactory._resolve_radius(args["size"])

        if args["size"] == "large":
            hx = extent * 0.05
            hy = extent * 0.75
            hz = extent * 1
        else:
            hx = hy = hz = extent * 0.5

        p000 = (-hx, -hy, -hz)
        p001 = (-hx, -hy,  hz)
        p010 = (-hx,  hy, -hz)
        p011 = (-hx,  hy,  hz)
        p100 = (hx, -hy, -hz)
        p101 = (hx, -hy,  hz)
        p110 = (hx,  hy, -hz)
        p111 = (hx,  hy,  hz)

        points = [p000, p100, p101, p001,
                  p000, p010, p110, p111,
                  p011, p010, p110, p100,
                  p101, p111, p011, p001]

        ctrl = cmds.curve(d=1, p=points, n=args["name"])

        shapes = cmds.listRelatives(ctrl, s=True, f=True) or []
        for s in shapes:
            cmds.setAttr(s + ".overrideEnabled", 1)
            cmds.setAttr(s + ".overrideColor", int(args["color_index"]))

        return ctrl

    @staticmethod
    def create_ctrl_pole_vector(**kwargs):
        args = dict(name="CTRL_Pole", size="medium", color_index=13)
        args.update(kwargs)

        extent = CtrlFactory._resolve_radius(args["size"])
        h = extent * 0.5

        points = [(-h, 0, 0), (h, 0, 0),
                  (0, 0, 0),
                  (0, -h, 0), (0, h, 0),
                  (0, 0, 0),
                  (0, 0, -h), (0, 0, h)]

        ctrl = cmds.curve(d=1, p=points, n=args["name"])

        shapes = cmds.listRelatives(ctrl, s=True, f=True) or []
        for s in shapes:
            cmds.setAttr(s + ".overrideEnabled", 1)
            cmds.setAttr(s + ".overrideColor", int(args["color_index"]))

        return ctrl

    @staticmethod
    def create_ctrl_ikfk_switch(**kwargs):
        args = dict(name="CTRL_IKFK", size="xsmall", color_index=6)
        args.update(kwargs)

        extent = CtrlFactory._resolve_radius(args["size"])
        h = extent * 0.5
        t = extent * 0.2

        points = [(-t,  h, 0), (t,  h, 0),
                  (t,  t, 0), (h,  t, 0),
                  (h, -t, 0), (t, -t, 0),
                  (t, -h, 0), (-t, -h, 0),
                  (-t, -t, 0), (-h, -t, 0),
                  (-h,  t, 0), (-t,  t, 0),
                  (-t,  h, 0)]

        ctrl = cmds.curve(d=1, p=points, n=args["name"])

        shapes = cmds.listRelatives(ctrl, s=True, f=True) or []
        for s in shapes:
            cmds.setAttr(s + ".overrideEnabled", 1)
            cmds.setAttr(s + ".overrideColor", int(args["color_index"]))

        return ctrl

    @staticmethod
    def create_ctrl_half_circle(**kwargs):
        args = dict(name="CTRL_halfCircle", size="medium", color_index=17)
        args.update(kwargs)

        radius = CtrlFactory._resolve_radius(args["size"])

        segments = 16
        points = []

        import math
        for i in range(segments + 1):
            angle = math.pi * (i / segments)  # 0 → 180°
            x = math.cos(angle) * radius
            z = math.sin(angle) * radius
            points.append((x, 0, z))

        ctrl = cmds.curve(d=1, p=points, n=args["name"])

        shapes = cmds.listRelatives(ctrl, s=True, f=True) or []
        for s in shapes:
            cmds.setAttr(s + ".overrideEnabled", 1)
            cmds.setAttr(s + ".overrideColor", int(args["color_index"]))

        return ctrl

    @staticmethod
    def create_ctrl_half_circle_ribbon(**kwargs):
        args = dict(name="CTRL_halfCircleRibbon", size="medium",
                    thickness=0.15, segments=24, color_index=17)
        args.update(kwargs)

        radius = CtrlFactory._resolve_radius(args["size"])
        thickness = radius * args["thickness"]
        segments = args["segments"]

        top = []
        bottom = []

        for i in range(segments + 1):
            angle = math.pi * (i / segments)

            y = math.cos(angle) * radius
            z = math.sin(angle) * radius

            px = thickness
            py = y
            pz = z

            top.append((px, py, -pz))
            bottom.append((-px, py, -pz))

        points = top + bottom[::-1] + [top[0]]

        ctrl = cmds.curve(d=1, p=points, n=args["name"])

        shapes = cmds.listRelatives(ctrl, s=True, f=True) or []
        for s in shapes:
            cmds.setAttr(s + ".overrideEnabled", 1)
            cmds.setAttr(s + ".overrideColor", int(args["color_index"]))

        return ctrl

    @staticmethod
    def create_ctrl_hip(**kwargs):

        args = dict(name="CTRL_Hip", size="medium",
                    color_index=17, segments=32)
        args.update(kwargs)

        radius = CtrlFactory._resolve_radius(args["size"])

        rx = radius
        rz = radius * 0.45

        seg = args["segments"]

        points = []

        for i in range(seg + 1):
            angle = 2 * math.pi * (i / seg)

            x = math.cos(angle) * rx
            z = math.sin(angle) * rz

            points.append((x, 0, z))

        ctrl1 = cmds.curve(d=1, p=points, n=args["name"])
        ctrl2 = cmds.curve(d=1, p=points)

        cmds.rotate(0, 90, 0, ctrl2, r=True)
        cmds.makeIdentity(ctrl2, apply=True, r=True)

        shapes = cmds.listRelatives(ctrl2, s=True, f=True) or []
        for s in shapes:
            cmds.parent(s, ctrl1, add=True, shape=True)

        cmds.delete(ctrl2)

        shapes = cmds.listRelatives(ctrl1, s=True, f=True) or []
        for s in shapes:
            cmds.setAttr(s + ".overrideEnabled", 1)
            cmds.setAttr(s + ".overrideColor", int(args["color_index"]))

        return ctrl1

    @staticmethod
    def create_ctrl_cross_arrow(**kwargs):

        args = dict(name="CTRL_Triangle", size="medium", color_index=14)
        args.update(kwargs)

        extent = CtrlFactory._resolve_radius(args["size"])
        r = extent * 0.5
        points = [(0, 0, r),
                  (-r, 0, -r),
                  (r, 0, -r),
                  (0, 0, r)]
        ctrl = cmds.curve(d=1, p=points, n=args["name"])
        cmds.move(0, 0, 25, ctrl, relative=True)
        cmds.xform(ctrl, ws=True, piv=(0, 0, 0))
        cmds.makeIdentity(ctrl, apply=True, t=True, r=True, s=True, n=0)
        line = cmds.curve(d=1,
                          p=[(0, 0, 0), (0, 0, 20)], n=args["name"] + "_line")
        line_shape = cmds.listRelatives(line, s=True, f=True)[0]
        cmds.parent(line_shape, ctrl, add=True, shape=True)
        cmds.delete(line)

        for i in range(1, 4):
            dup = cmds.duplicate(ctrl, rr=True)[0]
            cmds.rotate(0, 90 * i, 0, dup, r=True, os=True)
            cmds.makeIdentity(dup, apply=True, t=True, r=True, s=True, n=0)
            shapes = cmds.listRelatives(dup, s=True, f=True) or []
            cmds.parent(shapes, ctrl, add=True, shape=True)
            cmds.delete(dup)

        shapes = cmds.listRelatives(ctrl, s=True, f=True) or []
        for s in shapes:
            cmds.setAttr(s + ".overrideEnabled", 1)
            cmds.setAttr(s + ".overrideColor", int(args["color_index"]))

        return ctrl


class ControlBuilder:

    @staticmethod
    def build_root_fK_controls():

        root_joint = RIG_CTX.skeleton_root

        main_system = RigHelpers.get_or_create_group_chain(
            "Group", "controls", "MainSystem")

        root_joint = RIG_CTX.skeleton_root
        root_ctrl = CtrlFactory.create_ctrl_fk(
            name="FK_root", size=34.0, normal=(0, 0, 1))
        cmds.parent(root_ctrl, main_system)
        root_ctrl = cmds.ls(root_ctrl, long=True)[0]
        cmds.matchTransform(root_ctrl, root_joint)
        RigHelpers.bake_transform_to_opm(root_ctrl)
        RIG_CTX.control_registry.setdefault(
            "fk", {})["root"] = root_ctrl

    @staticmethod
    def build_limb_fK_controls():

        ControlBuilder.build_fk_chain_controls("limb", "medium")

    @staticmethod
    def build_limb_iK_controls():

        schema = UE5_SCHEMA.get("limb", {})

        deform_map = RIG_CTX.joint_registry.get("deform", {})

        ik_system = RigHelpers.get_or_create_group_chain(
            "Group", "controls", "IKSystem")

        for side, side_dict in schema.items():

            schema_grp = cmds.group(
                empty=True, name=f"ik_limb_{side}_ctrl_GRP", parent=ik_system)
            schema_base_joint = deform_map.get(f"limb_{side}")
            schema_grp = cmds.ls(schema_grp, long=True)[0]
            if schema_base_joint:
                cmds.matchTransform(schema_grp, schema_base_joint)
                RigHelpers.bake_transform_to_opm(schema_grp)
            RIG_CTX.group_registry.setdefault(
                "ik_ctrl", {})[f"limb_{side}"] = schema_grp

            for limb_name, chain in side_dict.items():
                if limb_name == "upperarm":
                    _, mid_name, end_name = chain[1:4]
                else:
                    _, mid_name, end_name = chain[0:3]

                mid_joint = deform_map.get(mid_name)
                end_joint = deform_map.get(end_name)

                chain_grp = cmds.group(
                    empty=True, name=f"ik_{limb_name}_{side}_ctrl_GRP", parent=schema_grp)
                chain_grp = cmds.ls(chain_grp, long=True)[0]
                chain_base_joint = deform_map.get(chain[0])
                cmds.matchTransform(chain_grp, chain_base_joint)
                RigHelpers.bake_transform_to_opm(chain_grp)
                RIG_CTX.group_registry.setdefault(
                    "ik_ctrl", {})[f"{limb_name}_{side}"] = chain_grp

                ik_ctrl = CtrlFactory.create_ctrl_ik(
                    name=f"{end_name}_ik_CTRL", size="medium")
                rot = limb_name == "thigh"
                cmds.matchTransform(ik_ctrl, end_joint,
                                    position=True, rotation=rot, scale=False)
                cmds.makeIdentity(ik_ctrl, apply=True,
                                  translate=False, rotate=True, scale=True, normal=0)
                cmds.parent(ik_ctrl, chain_grp)
                ik_ctrl = cmds.ls(ik_ctrl, long=True)[0]
                RigHelpers.bake_transform_to_opm(ik_ctrl)
                RIG_CTX.control_registry.setdefault(
                    "ik", {})[end_name] = ik_ctrl

                pole_ctrl = CtrlFactory.create_ctrl_pole_vector(
                    name=f"{mid_name}_pole_CTRL")
                cmds.matchTransform(pole_ctrl, mid_joint)
                offset = 40.0 if mid_name.startswith("calf") else -40.0
                offset *= 1 if mid_name.endswith("_r") else -1
                cmds.move(0, offset, 0, pole_ctrl,
                          relative=True, objectSpace=True)
                cmds.setAttr(f"{pole_ctrl}.rotate", 0, 0, 0)
                cmds.parent(pole_ctrl, chain_grp)
                pole_ctrl = cmds.ls(pole_ctrl, long=True)[0]
                RigHelpers.bake_transform_to_opm(pole_ctrl)
                RIG_CTX.control_registry.setdefault(
                    "ik", {})[mid_name] = pole_ctrl

    @staticmethod
    def build_limb_ikfk_controls():

        ControlBuilder.build_ikfk_controls("limb")

    @staticmethod
    def build_spine_fK_controls():

        ControlBuilder.build_fk_chain_controls("spine", "large")

    @staticmethod
    def build_spine_iK_controls():

        schema = UE5_SCHEMA.get("spine", {})

        deform_map = RIG_CTX.joint_registry.get("deform", {})

        ik_system = RigHelpers.get_or_create_group_chain(
            "Group", "controls", "IKSystem")

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                chain_grp = cmds.group(
                    empty=True, name=f"ik_{limb_name}_{side}_ctrl_GRP", parent=ik_system)
                chain_grp = cmds.ls(chain_grp, long=True)[0]
                base_joint = deform_map.get(chain[0])
                cmds.matchTransform(chain_grp, base_joint)
                RigHelpers.bake_transform_to_opm(chain_grp)
                RIG_CTX.group_registry.setdefault(
                    "ik_ctrl", {})[f"{limb_name}_{side}"] = chain_grp

                targets = chain[1:4]
                for joint_name in targets:
                    ik_ctrl = CtrlFactory.create_ctrl_ik(
                        name=f"{joint_name}_ik_CTRL", size="large")
                    ik_ctrl = cmds.ls(ik_ctrl, long=True)[0]
                    RIG_CTX.control_registry.setdefault(
                        "ik", {})[joint_name] = ik_ctrl

    @staticmethod
    def build_spine_ikfk_controls():

        ControlBuilder.build_ikfk_controls("spine")

    @staticmethod
    def build_hip_controls():

        hip_system = RigHelpers.get_or_create_group_chain(
            "Group", "driving_system", "HipSystem")

        deform_joints = RIG_CTX.joint_registry.get("deform", {})

        pelvis_fk_ctrl = RIG_CTX.control_registry.get("fk", {}).get("pelvis")
        pelvis_joint = deform_joints.get("pelvis")
        spine_01_joint = deform_joints.get("spine_01")

        hip_ctrl = CtrlFactory.create_ctrl_hip(
            name="pelvis_hip_CTRL", size="medium", color_index=17)
        cmds.matchTransform(hip_ctrl, pelvis_joint)
        cmds.move(0, 0, 30, hip_ctrl, relative=True, objectSpace=True)
        cmds.parent(hip_ctrl, pelvis_fk_ctrl)
        RigHelpers.bake_transform_to_opm(hip_ctrl)

        hip_offset_grp = cmds.group(
            empty=True, name="pelvis_hip_offset_GRP", parent=hip_ctrl)
        cmds.matchTransform(hip_offset_grp, spine_01_joint)
        RigHelpers.bake_transform_to_opm(hip_offset_grp)

        spine_01_group = cmds.group(
            empty=True, name="spine_01_hipFollow_GRP", parent=hip_system)
        cmds.matchTransform(spine_01_group, spine_01_joint)
        RigHelpers.bake_transform_to_opm(spine_01_group)

        pelvis_follow_group = cmds.group(
            empty=True, name="pelvis_hipFollow_GRP", parent=spine_01_group)
        cmds.matchTransform(pelvis_follow_group, pelvis_joint)
        RigHelpers.bake_transform_to_opm(pelvis_follow_group)

    @staticmethod
    def build_hand_controls():

        schema = UE5_SCHEMA.get("hand", {})

        deform_joints = RIG_CTX.joint_registry.get("deform", {})

        ControlBuilder.build_fk_chain_controls("hand", "small")

        fk_groups = RIG_CTX.group_registry.get("fk_ctrl", {})

        for side, side_dict in schema.items():
            joint_name = f"hand_{side}"
            deform_joint = deform_joints.get(joint_name)
            hand_ctrl = CtrlFactory.create_ctrl_half_circle(
                name=f"{joint_name}_ctrl", size="medium", color_index=17)
            cmds.matchTransform(hand_ctrl, deform_joint)
            rot_y = 90 if side == "l" else -90
            cmds.rotate(0, rot_y, 0, hand_ctrl,
                        relative=True, objectSpace=True)
            cmds.move(0, 0, 12, hand_ctrl, relative=True, objectSpace=True)

            group = fk_groups.get(f"hand_{side}")
            cmds.parent(hand_ctrl, group)
            hand_ctrl = cmds.ls(hand_ctrl, long=True)[0]
            RigHelpers.bake_transform_to_opm(hand_ctrl)
            RIG_CTX.control_registry.setdefault(
                "hand", {})[joint_name] = hand_ctrl

    @staticmethod
    def build_head_controls():

        ControlBuilder.build_fk_chain_controls("head", "medium")

    @staticmethod
    def build_fk_chain_controls(category, size):

        # print(f"##########################{category}##########################")

        schema = UE5_SCHEMA.get(category, {})

        deform_map = RIG_CTX.joint_registry.get("deform", {})

        fk_system = RigHelpers.get_or_create_group_chain(
            "Group", "controls", "FKSystem")

        for side, side_dict in schema.items():

            schema_grp = cmds.group(
                empty=True, name=f"{category}_{side}_ctrl_GRP", parent=fk_system)
            schema_base_joint = deform_map.get(f"{category}_{side}")
            schema_grp = cmds.ls(schema_grp, long=True)[0]
            if schema_base_joint:
                cmds.matchTransform(schema_grp, schema_base_joint)
                RigHelpers.bake_transform_to_opm(schema_grp)
            RIG_CTX.group_registry.setdefault(
                "fk_ctrl", {})[f"{category}_{side}"] = schema_grp

            for limb_name, chain in side_dict.items():

                chain_grp = cmds.group(
                    empty=True, name=f"fk_{limb_name}_{side}_ctrl_GRP", parent=schema_grp)
                chain_grp = cmds.ls(chain_grp, long=True)[0]
                chain_base_joint = deform_map.get(chain[0])
                cmds.matchTransform(chain_grp, chain_base_joint)
                RigHelpers.bake_transform_to_opm(chain_grp)
                RIG_CTX.group_registry.setdefault(
                    "fk_ctrl", {})[f"{limb_name}_{side}"] = chain_grp

                previous_ctrl = None

                for joint_name in chain:
                    joint = deform_map.get(joint_name)
                    if joint_name.startswith("clavicle"):
                        ctrl = CtrlFactory.create_ctrl_half_circle_ribbon(
                            name=f"{joint_name}_fk_CTRL", size=size, normal=(1, 0, 0))
                    else:
                        ctrl = CtrlFactory.create_ctrl_fk(
                            name=f"{joint_name}_fk_CTRL", size=size, normal=(1, 0, 0))

                    if previous_ctrl:
                        cmds.parent(ctrl, previous_ctrl)
                    else:
                        cmds.parent(ctrl, chain_grp)

                    cmds.matchTransform(ctrl, joint)
                    if joint_name.startswith("clavicle") and joint_name.endswith("_l"):
                        cmds.rotate(-180, 0, 0, ctrl,
                                    objectSpace=True, relative=True)
                        cmds.makeIdentity(
                            ctrl, apply=True, translate=True, rotate=True, scale=True)
                    cmds.setAttr(f"{ctrl}.visibility", keyable=False)
                    RigHelpers.bake_transform_to_opm(ctrl)
                    ctrl = cmds.ls(ctrl, long=True)[0]
                    RIG_CTX.control_registry.setdefault(
                        "fk", {})[joint_name] = ctrl

                    previous_ctrl = ctrl

    @staticmethod
    def build_ikfk_controls(category):

        schema = UE5_SCHEMA.get(category, {})

        deform_map = RIG_CTX.joint_registry.get("deform", {})

        ikfk_system = RigHelpers.get_or_create_group_chain(
            "Group", "controls", "IKFKSystem")

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                joint = deform_map[
                    chain[3] if category == "spine"else f"{limb_name}_{side}"]

                ctrl = CtrlFactory.create_ctrl_ikfk_switch(
                    name=f"{limb_name}_{side}_ikfk_CTRL")
                cmds.parent(ctrl, ikfk_system)
                ctrl = cmds.ls(ctrl, long=True)[0]

                cmds.matchTransform(ctrl, joint)
                cmds.setAttr(f"{ctrl}.rotate", 0, 0, 0)
                offset_x = 25.0 if category == "spine" else (
                    15.0 if side == "l"else -15.0)
                cmds.move(offset_x, 0, 0, ctrl,
                          relative=True, objectSpace=True)
                RigHelpers.bake_transform_to_opm(ctrl)
                RIG_CTX.control_registry.setdefault(
                    "ikfk", {})[f"{limb_name}_{side}"] = ctrl

                for attr in ("t", "r", "s"):
                    for axis in "xyz":
                        cmds.setAttr(f"{ctrl}.{attr}{axis}", lock=True,
                                     keyable=False, channelBox=False)
                cmds.setAttr(f"{ctrl}.visibility", lock=True,
                             keyable=False, channelBox=False)

                default_value = 0 if limb_name == "thigh" else 10
                cmds.addAttr(ctrl, longName="IKFKBlend", attributeType="double",
                             minValue=0, maxValue=10, defaultValue=default_value,
                             keyable=True)


RigHelpers = rig_runtime.RigHelpers
RIG_CTX = rig_runtime.RIG_CTX
UE5_SCHEMA = rig_runtime.UE5_SCHEMA
