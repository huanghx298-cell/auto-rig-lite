from PySide6 import QtWidgets, QtCore
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import shiboken6
import math

from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


class MySquareUI(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent or get_maya_window())

        self.setWindowTitle("Square UI")
        self.resize(300, 300)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(QtWidgets.QLabel("This is a dockable window"))

        self._add_button("Debug",
                         self.on_debug)
        self._add_button("AUTO RIG (UE5)",
                         self.on_build_ue5_auto_rig)

        self.layout.addStretch()

    def on_debug(self):
        cmds.undoInfo(openChunk=True)
        try:
            sel = cmds.ls(sl=True, type="joint", long=True)
            if not sel:
                raise RuntimeError("Please select skeleton root joint")

            CtrlFactory.create_ctrl_cross_arrow()
        except Exception as e:
            cmds.warning(str(e))
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_build_ue5_auto_rig(self):
        cmds.undoInfo(openChunk=True)
        try:
            sel = cmds.ls(sl=True, type="joint", long=True)
            if not sel:
                raise RuntimeError("Please select skeleton root joint")

            RigOps.build_ue5_auto_rig(sel[0])
        except Exception as e:
            cmds.warning(str(e))
        finally:
            cmds.undoInfo(closeChunk=True)

    def _add_button(self, label, callback):
        btn = QtWidgets.QPushButton(label)
        btn.clicked.connect(callback)
        self.layout.addWidget(btn)
        return btn


UE5_SCHEMA = {

    "spine": {
        "c": {
            "spine": ("spine_01", "spine_02", "spine_03", "spine_04", "spine_05")
        }
    },
    "neck": {
        "c": {
            "neck": ("neck_01", "neck_02", "head",)
        }
    },

    "hand": {
        "l": {
            "thumb":  ("thumb_01_l",  "thumb_02_l",  "thumb_03_l"),
            "index":  ("index_01_l",  "index_02_l",  "index_03_l"),
            "middle": ("middle_01_l", "middle_02_l", "middle_03_l"),
            "ring":   ("ring_01_l",   "ring_02_l",   "ring_03_l"),
            "pinky":  ("pinky_01_l",  "pinky_02_l",  "pinky_03_l"),
        },
        "r": {
            "thumb":  ("thumb_01_r",  "thumb_02_r",  "thumb_03_r"),
            "index":  ("index_01_r",  "index_02_r",  "index_03_r"),
            "middle": ("middle_01_r", "middle_02_r", "middle_03_r"),
            "ring":   ("ring_01_r",   "ring_02_r",   "ring_03_r"),
            "pinky":  ("pinky_01_r",  "pinky_02_r",  "pinky_03_r"),
        }
    },

    "foot": {
        "l": {
            "foot": ("foot_l", "ball_l"),
            "bank": ("bank_in_l", "bank_out_l"),
        },
        "r": {
            "foot": ("foot_r", "ball_r"),
            "bank": ("bank_in_r", "bank_out_r"),
        }
    },

    "clavicle": {
        "l": {
            "clavicle": ("clavicle_l",)
        },
        "r": {
            "clavicle": ("clavicle_r",)
        }
    },

    "limb": {
        "l": {
            "upperarm": ("upperarm_l", "lowerarm_l", "hand_l"),
            "thigh":    ("thigh_l", "calf_l", "foot_l", "ball_l"),
        },
        "r": {
            "upperarm": ("upperarm_r", "lowerarm_r", "hand_r"),
            "thigh":    ("thigh_r", "calf_r", "foot_r", "ball_r"),
        }
    },
    "twist": {
        "l": {
            "lowerarm": ("hand_l", "lowerarm_twist_02_l", "lowerarm_twist_01_l",),
            "upperarm": ("lowerarm_l", "upperarm_twist_01_l", "upperarm_twist_02_l"),
            "calf":     ("foot_l",     "calf_twist_02_l",     "calf_twist_01_l"),
            "thigh":    ("calf_l",    "thigh_twist_01_l",    "thigh_twist_02_l"),
        },
        "r": {
            "lowerarm": ("hand_r", "lowerarm_twist_02_r", "lowerarm_twist_01_r"),
            "upperarm": ("lowerarm_r", "upperarm_twist_01_r", "upperarm_twist_02_r"),
            "calf":     ("foot_r",     "calf_twist_02_r",     "calf_twist_01_r"),
            "thigh":    ("calf_r",    "thigh_twist_01_r",    "thigh_twist_02_r"),
        },
    },

}


class RigBuildContext:
    def __init__(self):
        self.skeleton_root = None
        self.control_registry = {}
        self.joint_registry = {}

    def clear(self):
        self.skeleton_root = None
        self.control_registry = {}
        self.joint_registry = {}


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
        cmds.move(0, 0, 25, ctrl, r=True)
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


class RigOps:

    @staticmethod
    def register_deform_skeleton(root):

        rig_root = RigHelpers.get_or_create_rig_root()
        skeleton_grp = RigHelpers.get_or_create_child(rig_root, "skeleton")
        deform_grp = RigHelpers.get_or_create_child(
            skeleton_grp, "deform_joints")

        new_root = cmds.parent(root, deform_grp)[0]
        new_root = cmds.ls(new_root, long=True)[0]

        all_joints = [new_root] + (
            cmds.listRelatives(new_root, ad=True, type="joint", f=True) or [])

        for j in all_joints:
            short = j.split("|")[-1]
            RIG_CTX.joint_registry.setdefault("deform", {})[short] = j
        return new_root

    @staticmethod
    def build_limb_FK_controls(root):

        rig_root = RigHelpers.get_or_create_rig_root()
        controls_grp = RigHelpers.get_or_create_child(rig_root, "controls")
        main_system = RigHelpers.get_or_create_child(
            controls_grp, "MainSystem")
        fk_system = RigHelpers.get_or_create_child(controls_grp, "FKSystem")

        main_system = cmds.ls(main_system, long=True)[0]
        fk_system = cmds.ls(fk_system, long=True)[0]

        all_joints = [root]+cmds.listRelatives(
            root, ad=True, type="joint", fullPath=True) or []
        joint_map = {j.split("|")[-1]: j for j in all_joints}

        root_ctrl = CtrlFactory.create_ctrl_fk(
            name="FK_root", size=34.0, normal=(0, 0, 1))
        cmds.matchTransform(root_ctrl, root)
        cmds.parent(root_ctrl, main_system)
        root_ctrl = cmds.ls(root_ctrl, long=True)[0]
        RIG_CTX.control_registry.setdefault("fk", {})["root"] = root_ctrl

        RigHelpers.build_fk_chain_controls(category="limb", joint_map=joint_map,
                                           parent_grp=fk_system, size="medium")
        RigHelpers.build_fk_chain_controls(category="hand", joint_map=joint_map,
                                           parent_grp=fk_system, size="small")

    @staticmethod
    def build_limb_IK_controls(root):

        schema = UE5_SCHEMA.get("limb", {})

        rig_root = RigHelpers.get_or_create_rig_root()
        controls_grp = RigHelpers.get_or_create_child(rig_root, "controls")
        ik_system = RigHelpers.get_or_create_child(controls_grp, "IKSystem")

        ik_system = cmds.ls(ik_system, long=True)[0]

        all_joints = [root]+cmds.listRelatives(
            root, ad=True, type="joint", fullPath=True) or []
        joint_map = {j.split("|")[-1]: j for j in all_joints}

        for side, side_dict in schema.items():

            side_grp = cmds.group(
                em=True, n=f"ik_limb_{side}_GRP", p=ik_system)
            side_grp = cmds.ls(side_grp, long=True)[0]
            RIG_CTX.control_registry.setdefault(
                "ik_groups", {})[f"limb_{side}_GRP"] = side_grp

            for limb_name, chain in side_dict.items():

                start_name = chain[0]
                mid_name = chain[1]
                end_name = chain[2]

                start_jnt = joint_map.get(start_name)
                mid_jnt = joint_map.get(mid_name)
                end_jnt = joint_map.get(end_name)

                limb_grp = cmds.group(
                    em=True, n=f"ik_{limb_name}_{side}_GRP", p=side_grp)
                limb_grp = cmds.ls(limb_grp, long=True)[0]
                RIG_CTX.control_registry.setdefault(
                    "ik_groups", {})[f"{limb_name}_{side}"] = limb_grp
                # cmds.matchTransform(limb_grp, start_jnt)
                # RigHelpers.freeze_to_offset_parent_matrix(limb_grp)

                ik_ctrl = CtrlFactory.create_ctrl_ik(
                    name=f"{end_name}_ik_CTRL", size="medium")
                cmds.matchTransform(ik_ctrl, end_jnt)
                if end_name == "foot_l":
                    cmds.rotate(-180, 90, -270, ik_ctrl, r=True, os=True)
                if end_name == "foot_r":
                    cmds.rotate(0, 90, 90, ik_ctrl, r=True, os=True)

                ik_ctrl = cmds.parent(ik_ctrl, limb_grp)[0]
                ik_ctrl = cmds.ls(ik_ctrl, long=True)[0]
                RigHelpers.freeze_to_offset_parent_matrix(ik_ctrl)
                if end_name.startswith("foot_"):
                    cmds.addAttr(ik_ctrl, ln="Roll",
                                 at="double", dv=0, keyable=True)
                    # cmds.addAttr(ik_ctrl, ln="Twist",
                    # at="double", dv=0, keyable=True)
                    cmds.addAttr(ik_ctrl, ln="Stretchy",
                                 at="double", min=0, max=10, dv=10, keyable=True)
                if end_name.startswith("hand_"):
                    cmds.addAttr(ik_ctrl, ln="Stretchy",
                                 at="double", min=0, max=10, dv=10, keyable=True)
                RIG_CTX.control_registry.setdefault(
                    "ik", {})[end_name] = ik_ctrl

                pole_ctrl = CtrlFactory.create_ctrl_pole_vector(
                    name=f"{mid_name}_pole_CTRL")
                cmds.matchTransform(pole_ctrl, mid_jnt)

                offset = 40.0 if mid_name.startswith("calf") else -40.0
                offset *= 1 if mid_name.endswith("_r") else -1

                cmds.move(0, offset, 0, pole_ctrl, r=True, os=True)
                cmds.setAttr(pole_ctrl + ".rotate", 0, 0, 0)

                cmds.addAttr(pole_ctrl, ln="Follow",
                             at="double", min=0, max=10, dv=10, keyable=True)
                cmds.addAttr(pole_ctrl, ln="Lock",
                             at="double", min=0, max=10, dv=0, keyable=True)

                pole_ctrl = cmds.parent(pole_ctrl, limb_grp)[0]
                pole_ctrl = cmds.ls(pole_ctrl, long=True)[0]
                RigHelpers.freeze_to_offset_parent_matrix(pole_ctrl)
                RIG_CTX.control_registry.setdefault(
                    "ik", {})[mid_name] = pole_ctrl

    @staticmethod
    def build_ikfk_switch_controls(root):

        rig_root = RigHelpers.get_or_create_rig_root()
        controls_grp = RigHelpers.get_or_create_child(rig_root, "controls")
        fkik_system = RigHelpers.get_or_create_child(
            controls_grp, "FKIKSystem")
        fkik_system = cmds.ls(fkik_system, long=True)[0]

        all_joints = [root] + (cmds.listRelatives(
            root, ad=True, type="joint", fullPath=True) or [])
        joint_map = {j.split("|")[-1]: j for j in all_joints}

        roots = []

        for side_dict in UE5_SCHEMA.get("limb", {}).values():
            for _, chain in side_dict.items():
                roots.append(chain[0])

        for side_dict in UE5_SCHEMA.get("spine", {}).values():
            for _, chain in side_dict.items():
                roots.append(chain[0])

        for root_name in roots:

            jnt = joint_map.get(root_name)

            ctrl = CtrlFactory.create_ctrl_ikfk_switch(
                name=f"{root_name}_ikfk_CTRL")
            cmds.matchTransform(ctrl, jnt)
            cmds.setAttr(ctrl + ".rotate", 0, 0, 0)

            if root_name.startswith("spine"):
                offset_x, offset_y = 20.0, 10.0
            else:
                offset_x = 10.0 if root_name.endswith("_l") else -10.0
                offset_y = 0

            cmds.move(offset_x, offset_y, 0, ctrl, r=True, os=True)

            ctrl = cmds.parent(ctrl, fkik_system)[0]
            ctrl = cmds.ls(ctrl, long=True)[0]
            RigHelpers.freeze_to_offset_parent_matrix(ctrl)

            RIG_CTX.control_registry.setdefault("ikfk", {})[root_name] = ctrl

            for attr in ("translateX", "translateY", "translateZ",
                         "rotateX", "rotateY", "rotateZ",
                         "scaleX", "scaleY", "scaleZ",
                         "visibility"):
                cmds.setAttr(f"{ctrl}.{attr}", lock=True,
                             keyable=False, channelBox=False)

            default_value = 10 if root_name.startswith("upperarm") else 0
            cmds.addAttr(ctrl, ln="IKFKBlend",
                         at="double", min=0, max=10, dv=default_value, keyable=True)
            cmds.addAttr(ctrl, ln="AutoVis", at="bool", dv=1)
            cmds.setAttr(ctrl + ".AutoVis", e=True,
                         keyable=False, channelBox=True)
            cmds.addAttr(ctrl, ln="FKVis", at="bool", dv=1, keyable=True)
            cmds.addAttr(ctrl, ln="IKVis", at="bool", dv=1, keyable=True)

    @staticmethod
    def build_limb_ik_fk_skeletons(root):

        RigHelpers.build_schema_skeleton(root, "limb", "ik")
        RigHelpers.build_schema_skeleton(root, "limb", "fk")

    @staticmethod
    def build_limb_ikfk_deform_drivers():

        schema = UE5_SCHEMA.get("limb", {})

        ikfk_ctrls = RIG_CTX.control_registry.get("ikfk", {})
        fk_ctrls = RIG_CTX.control_registry.get("fk", {})
        ik_ctrls = RIG_CTX.control_registry.get("ik", {})

        fk_joints = RIG_CTX.joint_registry.get("fk", {})
        ik_joints = RIG_CTX.joint_registry.get("ik", {})
        deform_joints = RIG_CTX.joint_registry.get("deform", {})

        for side, side_dict in schema.items():
            for limb_root, chain in side_dict.items():
                ctrl_key = chain[0]

                ctrl = ikfk_ctrls.get(ctrl_key)
                if not ctrl:
                    continue

                ctrl_short = ctrl.split("|")[-1]

                md = cmds.createNode(
                    "multiplyDivide", n=f"{ctrl_key}_IKFKBlend_MD")
                cmds.setAttr(md + ".input2X", 0.1)
                cmds.connectAttr(
                    f"{ctrl_short}.IKFKBlend", md + ".input1X", force=True)

                rev = cmds.createNode("reverse", n=f"{ctrl_key}_IKFKBlend_REV")
                cmds.connectAttr(md + ".outputX", rev + ".inputX", force=True)

                for joint_name in chain:
                    fk = fk_joints.get(joint_name)
                    ik = ik_joints.get(joint_name)
                    deform = deform_joints.get(joint_name)

                    fk_ctrl = fk_ctrls.get(joint_name)
                    ik_ctrl = ik_ctrls.get(joint_name)

                    constraint = cmds.parentConstraint(
                        fk, ik, deform, mo=False)[0]

                    w0_attr = cmds.listAttr(constraint, string="*W0")[0]
                    w1_attr = cmds.listAttr(constraint, string="*W1")[0]

                    cmds.connectAttr(
                        md + ".outputX", f"{constraint}.{w0_attr}", force=True)
                    cmds.connectAttr(
                        rev + ".outputX", f"{constraint}.{w1_attr}", force=True)

                    cmds.connectAttr(
                        md + ".outputX", fk_ctrl + ".visibility", force=True)
                    if joint_name in (chain[1], chain[2]):
                        cmds.connectAttr(
                            rev + ".outputX", ik_ctrl + ".visibility", force=True)

    @staticmethod
    def build_limb_fk_joint_drivers():

        fk_ctrls = RIG_CTX.control_registry.get("fk", {})
        fk_joints = RIG_CTX.joint_registry.get("fk", {})
        deform_joints = RIG_CTX.joint_registry.get("deform", {})

        limb_schema = UE5_SCHEMA.get("limb", {})

        for _, side_dict in limb_schema.items():
            for _, chain in side_dict.items():

                for joint_name in chain:

                    ctrl = fk_ctrls.get(joint_name)
                    joint = fk_joints.get(joint_name)

                    cmds.connectAttr(
                        f"{ctrl}.translate", f"{joint}.translate", force=True)
                    cmds.connectAttr(
                        f"{ctrl}.rotate", f"{joint}.rotate", force=True)

        hand_schema = UE5_SCHEMA.get("hand", {})

        for _, side_dict in hand_schema.items():
            for _, chain in side_dict.items():

                for joint_name in chain:

                    ctrl = fk_ctrls.get(joint_name)
                    joint = deform_joints.get(joint_name)

                    cmds.parentConstraint(ctrl, joint, mo=False)

    @staticmethod
    def build_limb_ik_joint_drivers():

        limb_schema = UE5_SCHEMA.get("limb", {})

        joint_map = RIG_CTX.joint_registry.get("ik", {})
        ctrl_map = RIG_CTX.control_registry.get("ik", {})

        for _, side_dict in limb_schema.items():
            for limb_name, chain in side_dict.items():

                start_name = chain[0]
                end_name = chain[2]

                start_joint = joint_map.get(start_name)
                end_joint = joint_map.get(end_name)

                ik_handle, effector = cmds.ikHandle(sj=start_joint, ee=end_joint,
                                                    sol="ikRPsolver",
                                                    n=f"{end_name}_IKH")

                ik_ctrl = ctrl_map.get(end_name)

                if limb_name != "thigh":
                    cmds.orientConstraint(ik_ctrl, end_joint, mo=False)
                cmds.parent(ik_handle, ik_ctrl)

        for _, side_dict in limb_schema.items():
            for _, chain in side_dict.items():

                mid_name = chain[1]
                end_name = chain[2]

                ik_ctrl = ctrl_map.get(end_name)
                pole_ctrl = ctrl_map.get(mid_name)

                ik_handles = cmds.listRelatives(
                    ik_ctrl, ad=True, type="ikHandle", fullPath=True) or []

                ikh = ik_handles[0]

                cmds.poleVectorConstraint(pole_ctrl, ikh)

    @staticmethod
    def build_spine_ik_fk_skeletons(root):

        RigHelpers.build_schema_skeleton(root, "spine", "ik")
        RigHelpers.build_schema_skeleton(root, "spine", "fk")

    @staticmethod
    def build_spine_fk_joint_drivers(root):

        spine_schema = UE5_SCHEMA.get("spine", {})

        rig_root = RigHelpers.get_or_create_rig_root()
        controls_grp = RigHelpers.get_or_create_child(rig_root, "controls")
        fk_system = RigHelpers.get_or_create_child(controls_grp, "FKSystem")

        fk_system = cmds.ls(fk_system, long=True)[0]

        all_joints = [root]+cmds.listRelatives(
            root, ad=True, type="joint", fullPath=True) or []
        joint_map = {j.split("|")[-1]: j for j in all_joints}

        RigHelpers.build_fk_chain_controls(category="spine", joint_map=joint_map,
                                           parent_grp=fk_system, size="large")

        fk_ctrls = RIG_CTX.control_registry["fk"]
        fk_joints = RIG_CTX.joint_registry["fk"]

        for _, side_dict in spine_schema.items():
            for _, chain in side_dict.items():

                for joint_name in chain[:-1]:

                    fk_joint = fk_joints.get(joint_name)
                    fk_ctrl = fk_ctrls.get(joint_name)

                    cmds.connectAttr(
                        f"{fk_ctrl}.translate", f"{fk_joint}.translate", force=True)
                    cmds.connectAttr(
                        f"{fk_ctrl}.rotate", f"{fk_joint}.rotate", force=True)

    @staticmethod
    def create_spine_spline_ik():

        spine_schema = UE5_SCHEMA.get("spine", {})
        ik_joints = RIG_CTX.joint_registry.get("ik", {})

        rig_root = RigHelpers.get_or_create_rig_root()
        driving_root = RigHelpers.get_or_create_child(
            rig_root, "driving_system")
        spine_system = RigHelpers.get_or_create_child(driving_root, "spine")

        for _, side_dict in spine_schema.items():
            for _, chain in side_dict.items():
                spine_chain = chain
        start_joint = ik_joints[spine_chain[0]]
        end_joint = ik_joints[spine_chain[-1]]
        ikh, effector, curve = cmds.ikHandle(
            sj=start_joint, ee=end_joint,
            sol="ikSplineSolver",
            createCurve=True, parentCurve=False, simplifyCurve=False,
            n="spine_IKH")
        cmds.parent(ikh, spine_system)
        cmds.parent(curve, spine_system)
        ikh = cmds.ls(ikh, long=True)[0]
        curve = cmds.ls(curve, long=True)[0]

        return curve, ikh

    @staticmethod
    def create_spine_follow_joints(curve):

        spine_schema = UE5_SCHEMA.get("spine", {})
        ik_joints = RIG_CTX.joint_registry.get("ik", {})

        rig_root = RigHelpers.get_or_create_rig_root()
        driving_root = RigHelpers.get_or_create_child(
            rig_root, "driving_system")
        spine_system = RigHelpers.get_or_create_child(driving_root, "spine")
        follow_grp = RigHelpers.get_or_create_child(
            spine_system, "follow_joints")

        follow_grp = cmds.ls(follow_grp, long=True)[0]
        RIG_CTX.joint_registry.setdefault(
            "driver_groups", {})["spine_follow"] = follow_grp

        for _, side_dict in spine_schema.items():
            for _, chain in side_dict.items():
                spine_chain = chain
        start_joint = ik_joints[spine_chain[0]]
        end_joint = ik_joints[spine_chain[-2]]

        start_jnt = cmds.duplicate(
            start_joint, parentOnly=True, name="spine_start_follow_JNT")[0]
        end_jnt = cmds.duplicate(
            end_joint, parentOnly=True, name="spine_end_follow_JNT")[0]
        cmds.parent(start_jnt, follow_grp)
        cmds.parent(end_jnt, follow_grp)
        start_jnt = cmds.ls(start_jnt, long=True)[0]
        end_jnt = cmds.ls(end_jnt, long=True)[0]

        mid_info = cmds.createNode("pointOnCurveInfo", n="spine_mid_POCI")
        cmds.connectAttr(
            curve + ".worldSpace[0]", mid_info + ".inputCurve", force=True)
        cmds.setAttr(mid_info + ".turnOnPercentage", 1)
        cmds.setAttr(mid_info + ".parameter", 0.25)
        mid_pos = cmds.getAttr(mid_info + ".position")[0]
        mid_tangent = cmds.getAttr(mid_info + ".tangent")[0]
        cmds.delete(mid_info)

        mid_jnt = cmds.joint(n="spine_mid_follow_JNT", p=mid_pos)
        cmds.parent(mid_jnt, follow_grp)
        mid_jnt = cmds.ls(mid_jnt, long=True)[0]

        default_vec = (1, 0, 0)
        rot = cmds.angleBetween(v1=default_vec, v2=mid_tangent, euler=True)
        cmds.setAttr(mid_jnt + ".rotateX", -90)
        cmds.setAttr(mid_jnt + ".rotateY", rot[1])
        cmds.setAttr(mid_jnt + ".rotateZ", rot[2])

        driver_joints = [start_jnt, mid_jnt, end_jnt]
        for jnt in driver_joints:
            RigHelpers.bake_joint_to_attributes(jnt)
            RigHelpers.freeze_to_offset_parent_matrix(jnt)

        return driver_joints

    @staticmethod
    def build_spine_ik_controls(driver_joints, curve, ikh):

        rig_root = RigHelpers.get_or_create_rig_root()
        controls_grp = RigHelpers.get_or_create_child(rig_root, "controls")
        ik_system = RigHelpers.get_or_create_child(controls_grp, "IKSystem")
        ik_system = cmds.ls(ik_system, long=True)[0]
        spine_ik_grp = RigHelpers.get_or_create_child(
            ik_system, "ik_spine_c_GRP")
        spine_ik_grp = cmds.ls(spine_ik_grp, long=True)[0]
        RIG_CTX.control_registry.setdefault(
            "ik_groups", {})["spine_c"] = spine_ik_grp

        ik_ctrl_map = {}

        for jnt in driver_joints:

            short = jnt.split("|")[-1]
            base_name = short[:-4]

            ctrl = CtrlFactory.create_ctrl_ik(
                name=base_name + "_CTRL",  size="large", color_index=13)
            cmds.matchTransform(ctrl, jnt)
            cmds.parent(ctrl, spine_ik_grp)
            ctrl = cmds.ls(ctrl, long=True)[0]
            RigHelpers.freeze_to_offset_parent_matrix(ctrl)
            RIG_CTX.control_registry.setdefault("ik", {})[base_name] = ctrl

            ik_ctrl_map[base_name] = ctrl

        end_ctrl = ik_ctrl_map.get("spine_end_follow")
        cmds.addAttr(end_ctrl, ln="Stretchy",
                     at="double", min=0, max=10, dv=10)
        cmds.setAttr(f"{end_ctrl}.Stretchy", e=True, keyable=True)

        ## Create and register IK spine controls for follow joints ##

        for jnt in driver_joints:
            short = jnt.split("|")[-1]
            base_name = short[:-4]
            ctrl = ik_ctrl_map[base_name]
            cmds.connectAttr(
                ctrl + ".translate", jnt + ".translate", force=True)
            cmds.connectAttr(
                ctrl + ".rotate", jnt + ".rotate", force=True)

        cmds.skinCluster(driver_joints, curve,
                         tsb=True, mi=1, nw=1,
                         n="spine_curve_skinCluster")[0]

        ## IK ctrls → follow joints → skinCluster → spline curve ##
        ## end IK joint via orientConstraint ##

        start_ctrl = ik_ctrl_map["spine_start_follow"]
        end_ctrl = ik_ctrl_map["spine_end_follow"]
        cmds.connectAttr(start_ctrl + ".rotateX", ikh + ".roll", force=True)

        md = cmds.createNode("multiplyDivide", n="spine_start_neg_MD")
        cmds.setAttr(md + ".input2X", -1)
        cmds.connectAttr(start_ctrl + ".rotateX", md + ".input1X", force=True)

        pma = cmds.createNode("plusMinusAverage", n="spine_twist_sum_PMA")
        cmds.setAttr(pma + ".operation", 1)
        cmds.connectAttr(md + ".outputX", pma + ".input1D[0]", force=True)
        cmds.connectAttr(
            end_ctrl + ".rotateX", pma + ".input1D[1]", force=True)
        cmds.connectAttr(pma + ".output1D", ikh + ".twist", force=True)

        ## Setup spline IK roll & twist control ##

    @staticmethod
    def build_spine_ik_joint_drivers():

        curve, ikh = _run_step(
            RigOps.create_spine_spline_ik)
        driver_joints = _run_step(
            RigOps.create_spine_follow_joints,
            curve)
        _run_step(RigOps.build_spine_ik_controls,
                  driver_joints, curve, ikh)

    @staticmethod
    def build_spine_deform_drivers():

        spine_schema = UE5_SCHEMA.get("spine", {})

        ikfk_ctrls = RIG_CTX.control_registry["ikfk"]
        fk_ctrls = RIG_CTX.control_registry["fk"]
        ik_ctrls = RIG_CTX.control_registry["ik"]

        fk_joints = RIG_CTX.joint_registry["fk"]
        ik_joints = RIG_CTX.joint_registry["ik"]
        deform_joints = RIG_CTX.joint_registry["deform"]

        spine_root = UE5_SCHEMA["spine"]["c"]["spine"][0]
        ctrl = ikfk_ctrls[spine_root]
        ctrl_short = ctrl.split("|")[-1]

        md = cmds.createNode("multiplyDivide", n="spine_IKFKBlend_MD")
        cmds.setAttr(md + ".input2X", 0.1)
        cmds.connectAttr(f"{ctrl_short}.IKFKBlend",
                         md + ".input1X", force=True)

        rev = cmds.createNode("reverse", n="spine_IKFKBlend_REV")
        cmds.connectAttr(md + ".outputX", rev + ".inputX", force=True)

        for _, side_dict in spine_schema.items():
            for _, chain in side_dict.items():
                for joint_name in chain:

                    deform = deform_joints[joint_name]
                    fk = fk_joints[joint_name]
                    ik = ik_joints[joint_name]
                    constraint = cmds.parentConstraint(
                        fk, ik, deform, mo=False)[0]
                    w0_attr = cmds.listAttr(constraint, string="*W0")[0]
                    w1_attr = cmds.listAttr(constraint, string="*W1")[0]
                    cmds.connectAttr(
                        md + ".outputX", f"{constraint}.{w0_attr}", force=True)
                    cmds.connectAttr(
                        rev + ".outputX", f"{constraint}.{w1_attr}", force=True)

                    fk_ctrl = fk_ctrls[joint_name]
                    cmds.connectAttr(
                        md + ".outputX", fk_ctrl + ".visibility", force=True)

        for key in ("spine_start_follow", "spine_mid_follow", "spine_end_follow"):
            ctrl = ik_ctrls.get(key)
            cmds.connectAttr(
                rev + ".outputX", ctrl + ".visibility", force=True)

    @staticmethod
    def build_hand_controls():

        hand_schema = UE5_SCHEMA.get("hand", {})
        deform_joints = RIG_CTX.joint_registry.get("deform", {})
        fk_groups = RIG_CTX.control_registry.get("fk_groups", {})

        for side in hand_schema:

            jnt_name = f"hand_{side}"
            hand_joint = deform_joints.get(jnt_name)

            ctrl = CtrlFactory.create_ctrl_half_circle(
                name=f"{jnt_name}_ctrl", size="medium", color_index=17)

            cmds.matchTransform(ctrl, hand_joint)

            if side == "l":
                cmds.rotate(0, 90, 0, ctrl, r=True, os=True)
            else:
                cmds.rotate(0, -90, 0, ctrl, r=True, os=True)

            cmds.move(0, 0, 12, ctrl, r=True, os=True)

            grp = fk_groups.get(f"hand_{side}_GRP")
            cmds.parent(ctrl, grp)
            ctrl = cmds.ls(ctrl, long=True)[0]

            RigHelpers.freeze_to_offset_parent_matrix(ctrl)

            RIG_CTX.control_registry.setdefault("hand", {})[jnt_name] = ctrl

    @staticmethod
    def build_hand_spread_attributes():

        hand_schema = UE5_SCHEMA.get("hand", {})
        hand_ctrls = RIG_CTX.control_registry.get("hand", {})
        finger_ctrls = RIG_CTX.control_registry.get("fk", {})

        weights = {"index":  1.0,
                   "middle": 0.0,
                   "ring": -1.0,
                   "pinky": -2.0, }

        for hand_key, ctrl in hand_ctrls.items():

            side = hand_key.split("_")[1]
            side_chains = hand_schema.get(side, {})

            cmds.addAttr(ctrl, ln="Spread",
                         at="double", min=-5, max=10, dv=0, keyable=True)

            for finger_name, chain in side_chains.items():
                if finger_name == "thumb":
                    continue
                w = weights.get(finger_name)

                base_joint = chain[0]
                fk_ctrl = finger_ctrls.get(base_joint)

                md = cmds.createNode("multiplyDivide",
                                     n=f"{hand_key}_{finger_name}_Spread_MD")
                cmds.setAttr(f"{md}.input2X", w)
                cmds.connectAttr(f"{ctrl}.Spread",
                                 f"{md}.input1X", force=True)
                cmds.connectAttr(f"{md}.outputX",
                                 f"{fk_ctrl}.rotateY", force=True)

    @staticmethod
    def build_hand_curl_attributes():

        hand_schema = UE5_SCHEMA.get("hand", {})
        hand_ctrls = RIG_CTX.control_registry.get("hand", {})
        finger_ctrls = RIG_CTX.control_registry.get("fk", {})

        for hand_key, ctrl in hand_ctrls.items():

            side = hand_key.split("_")[1]
            side_chains = hand_schema.get(side, {})

            thumb_chain = side_chains.get("thumb")
            if thumb_chain:

                attr_name = "Thumb_Curl"

                cmds.addAttr(ctrl, ln=attr_name,
                             at="double", min=-2, max=10, dv=0, keyable=True)

                md01 = cmds.createNode(
                    "multiplyDivide", n=f"{hand_key}_thumb01_Curl_MD")
                cmds.setAttr(f"{md01}.input2X", 4)
                cmds.connectAttr(f"{ctrl}.{attr_name}",
                                 f"{md01}.input1X", force=True)
                fk_ctrl_01 = finger_ctrls.get(thumb_chain[0])
                cmds.connectAttr(f"{md01}.outputX",
                                 f"{fk_ctrl_01}.rotateZ", force=True)

                md23 = cmds.createNode(
                    "multiplyDivide", n=f"{hand_key}_thumb23_Curl_MD")
                cmds.setAttr(f"{md23}.input2X", 8)
                cmds.connectAttr(f"{ctrl}.{attr_name}",
                                 f"{md23}.input1X", force=True)
                for joint_name in thumb_chain[1:]:
                    fk_ctrl = finger_ctrls.get(joint_name)
                    cmds.connectAttr(f"{md23}.outputX",
                                     f"{fk_ctrl}.rotateZ", force=True)

            for finger_name, chain in side_chains.items():
                if finger_name == "thumb":
                    continue

                attr_name = f"{finger_name.capitalize()}_Curl"

                cmds.addAttr(ctrl, ln=attr_name,
                             at="double", min=-2, max=10, dv=0)
                cmds.setAttr(f"{ctrl}.{attr_name}", e=True, keyable=True)

                md_name = f"{hand_key}_{finger_name}_Curl_MD"
                md = cmds.createNode("multiplyDivide", n=md_name)
                cmds.setAttr(f"{md}.input2X", 9)
                cmds.connectAttr(f"{ctrl}.{attr_name}",
                                 f"{md}.input1X", force=True)
                for joint_name in chain:
                    fk_ctrl = finger_ctrls.get(joint_name)
                    cmds.connectAttr(f"{md}.outputX",
                                     f"{fk_ctrl}.rotateZ", force=True)

            for attr in ("translateX", "translateY", "translateZ",
                         "rotateX", "rotateY", "rotateZ",
                         "scaleX", "scaleY", "scaleZ",
                         "visibility"):
                cmds.setAttr(f"{ctrl}.{attr}", lock=True,
                             keyable=False, channelBox=False)

    @staticmethod
    def connect_hand_to_finger_groups():

        hand_schema = UE5_SCHEMA.get("hand", {})
        fk_groups = RIG_CTX.control_registry.get("fk_groups", {})
        deform_joints = RIG_CTX.joint_registry.get("deform", {})

        for side, _ in hand_schema.items():

            grp = fk_groups.get(f"hand_{side}_GRP")
            hand_joint = deform_joints.get(f"hand_{side}")

            cmds.parentConstraint(hand_joint, grp, mo=True)

    @staticmethod
    def build_pole_vector_space_blend():

        limb_schema = UE5_SCHEMA.get("limb", {})
        ik_ctrls = RIG_CTX.control_registry.get("ik", {})

        for side, side_dict in limb_schema.items():
            for limb_name, chain in side_dict.items():

                mid_name = chain[1]
                end_name = chain[2]

                ik_ctrl = ik_ctrls.get(end_name)
                pole_ctrl = ik_ctrls.get(mid_name)

                ik_short = ik_ctrl.split("|")[-1]
                pole_short = pole_ctrl.split("|")[-1]

                follow_grp = cmds.group(
                    em=True, n=f"{end_name}_poleFollow_GRP")
                cmds.matchTransform(follow_grp, ik_ctrl,
                                    pos=True, rot=False, scl=False)
                follow_grp = cmds.parent(follow_grp, ik_ctrl)[0]

                blend = cmds.createNode(
                    "blendMatrix", n=f"{ik_short}_space_BM")
                pole_initial_opm = cmds.getAttr(
                    pole_ctrl + ".offsetParentMatrix")
                cmds.setAttr(blend + ".inputMatrix",
                             *pole_initial_opm, type="matrix")

                initial_matrix = cmds.getAttr(follow_grp + ".worldMatrix[0]")
                inv = cmds.createNode("inverseMatrix",
                                      n=f"{end_name}_space_inv_MTX")
                cmds.setAttr(inv + ".inputMatrix",
                             *initial_matrix, type="matrix")
                mm = cmds.createNode("multMatrix",
                                     n=f"{end_name}_space_delta_MM")
                cmds.connectAttr(follow_grp + ".worldMatrix[0]",
                                 mm + ".matrixIn[0]", force=True)
                cmds.connectAttr(inv + ".outputMatrix",
                                 mm + ".matrixIn[1]", force=True)

                dcm = cmds.createNode("decomposeMatrix",
                                      n=f"{mid_name}_follow_DCM")
                cmds.connectAttr(mm + ".matrixSum",
                                 dcm + ".inputMatrix", force=True)
                cm = cmds.createNode("composeMatrix",
                                     n=f"{mid_name}_follow_CM")
                cmds.connectAttr(dcm + ".outputTranslate",
                                 cm + ".inputTranslate", force=True)

                mm2 = cmds.createNode("multMatrix",
                                      n=f"{mid_name}_pole_follow_MM")
                cmds.setAttr(mm2 + ".matrixIn[1]",
                             *pole_initial_opm, type="matrix")
                cmds.connectAttr(cm + ".outputMatrix",
                                 mm2 + ".matrixIn[0]", force=True)

                cmds.connectAttr(mm2 + ".matrixSum",
                                 blend + ".target[0].targetMatrix", force=True)
                cmds.connectAttr(blend + ".outputMatrix",
                                 pole_ctrl + ".offsetParentMatrix", force=True)

                md = cmds.createNode(
                    "multiplyDivide", n=f"{pole_short}_follow_normalize_MD")
                cmds.setAttr(md + ".input2X", 0.1)
                cmds.connectAttr(pole_ctrl + ".Follow",
                                 md + ".input1X", force=True)
                cmds.connectAttr(md + ".outputX",
                                 blend + ".envelope", force=True)

    @staticmethod
    def build_foot_roll_drivers():

        schema = UE5_SCHEMA.get("foot", {})

        deform_joint_map = RIG_CTX.joint_registry.get("deform", {})
        ik_joint_map = RIG_CTX.joint_registry.get("ik", {})
        ik_ctrl_map = RIG_CTX.control_registry.get("ik", {})

        rig_root_grp = RigHelpers.get_or_create_rig_root()
        driving_grp = RigHelpers.get_or_create_child(
            rig_root_grp, "driving_system")
        foot_roll_grp = RigHelpers.get_or_create_child(
            driving_grp, "foot_roll_system")

        for _, side_dict in schema.items():
            for limb_name, chain in side_dict.items():
                if limb_name != "foot":
                    continue

                base_short, ball_short = chain

                deform_joint_base = deform_joint_map.get(base_short)
                deform_joint_ball = deform_joint_map.get(ball_short)
                ik_joint_base = ik_joint_map.get(base_short)
                ik_joint_ball = ik_joint_map.get(ball_short)
                ik_ctrl = ik_ctrl_map.get(base_short)

                grp = cmds.group(
                    em=True, name=f"footRoll_{chain[0]}_GRP")
                grp = cmds.parent(grp, foot_roll_grp)[0]
                grp = cmds.ls(f"footRoll_{chain[0]}_GRP", long=True)[0]
                RIG_CTX.joint_registry.setdefault(
                    "footRoll_groups", {})[base_short] = grp

                cmds.parentConstraint(ik_ctrl, grp, mo=True)

                ball_ikh, _ = cmds.ikHandle(sj=ik_joint_base, ee=ik_joint_ball,
                                            sol="ikSCsolver",
                                            n=f"{ball_short}_footRoll_IKH")
                cmds.parent(ball_ikh, grp)
                ball_ikh = cmds.ls(f"{ball_short}_footRoll_IKH", long=True)[0]

                ball_fr_jnt = RigHelpers.create_joint(
                    name=f"{ball_short}_footRoll_JNT",
                    parent=grp, match_target=deform_joint_ball)
                base_fr_jnt = RigHelpers.create_joint(
                    name=f"{base_short}_footRoll_JNT",
                    parent=ball_fr_jnt, match_target=deform_joint_base)
                cancel_fr_jnt = RigHelpers.create_joint(
                    name=f"{ball_short}_footRollCancel_JNT",
                    parent=ball_fr_jnt, match_target=deform_joint_ball)

                inv_md = cmds.createNode("multiplyDivide",
                                         n=f"{base_short}_footRoll_INV_MD")
                cmds.setAttr(inv_md + ".input2X", -1)
                cmds.connectAttr(f"{ik_ctrl}.Roll",
                                 inv_md + ".input1X", force=True)
                cmds.connectAttr(inv_md + ".outputX",
                                 f"{ball_fr_jnt}.rotateZ", force=True)

                cmds.connectAttr(f"{ball_fr_jnt}.rotateZ",
                                 f"{base_fr_jnt}.rotateZ", force=True)

                cancel_md = cmds.createNode(
                    "multiplyDivide", n=f"{base_short}_footRollCancel_INV_MD")
                cmds.setAttr(cancel_md + ".input2X", -1)
                cmds.connectAttr(f"{ball_fr_jnt}.rotateZ",
                                 cancel_md + ".input1X", force=True)
                cmds.connectAttr(cancel_md + ".outputX",
                                 f"{cancel_fr_jnt}.rotateZ", force=True)

                ik_handle = cmds.listRelatives(
                    ik_ctrl, type="ikHandle", fullPath=True)[0]
                cmds.parentConstraint(base_fr_jnt, ik_handle, mo=False)
                cmds.connectAttr(f"{ik_ctrl}.Roll",
                                 f"{ik_joint_ball}.rotateZ", force=True)

    @staticmethod
    def build_twist_skeleton(root):

        schema = UE5_SCHEMA.get("twist", {})
        deform_map = RIG_CTX.joint_registry.get("deform", {})

        rig_root = RigHelpers.get_or_create_rig_root()
        driving_root = RigHelpers.get_or_create_child(
            rig_root, "driving_system")
        twist_root = RigHelpers.get_or_create_child(
            driving_root, "twist_system")
        twist_root = cmds.ls(twist_root, long=True)[0]

        new_root = cmds.duplicate(root, rr=True)[0]
        new_root = cmds.ls(new_root, long=True)[0]
        full_hierarchy = [new_root] + (
            cmds.listRelatives(new_root, ad=True, type="joint", f=True) or [])
        joint_by_short = {j.split("|")[-1]: j for j in full_hierarchy}

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                base_joint = joint_by_short.get(f"{limb_name}_{side}")
                de_joint = deform_map.get(f"{limb_name}_{side}")

                limb_grp_name = f"twist_{limb_name}_{side}_GRP"
                limb_grp = cmds.group(em=True, n=limb_grp_name, p=twist_root)
                limb_grp = cmds.ls(limb_grp, long=True)[0]
                RIG_CTX.joint_registry.setdefault(
                    "twist_groups", {})[f"{limb_name}_{side}"] = limb_grp
                cmds.matchTransform(limb_grp, de_joint)
                RigHelpers.freeze_to_offset_parent_matrix(limb_grp)
                cmds.parent(base_joint, limb_grp)

                limb_root = cmds.listRelatives(
                    limb_grp, c=True, type="joint", f=True)[0]
                limb_joints = [limb_root] + (
                    cmds.listRelatives(limb_root, ad=True, type="joint", f=True) or [])
                limb_joints.sort(key=lambda x: x.count("|"), reverse=True)

                twist_joints = chain[1:]
                keep_set = {f"{limb_name}_{side}"} | set(twist_joints)
                rename_queue = []

                for joint in limb_joints:
                    short = joint.split("|")[-1]
                    if short in keep_set:
                        rename_queue.append((joint, short))
                    else:
                        cmds.delete(joint)

                rename_queue.sort(key=lambda x: x[0].count("|"), reverse=True)

                for joint, short in rename_queue:
                    cmds.rename(joint, f"{short}_twist_JNT")

                for joint, short in reversed(rename_queue):
                    new_joint = cmds.ls(f"{short}_twist_JNT", long=True)[0]
                    deform_joint = deform_map.get(short)
                    cmds.matchTransform(new_joint, deform_joint)
                    RigHelpers.freeze_to_offset_parent_matrix(new_joint)
                    cmds.setAttr(new_joint + ".jointOrient", 0, 0, 0)
                    # cmds.setAttr(new_joint + ".visibility", 0)
                    RIG_CTX.joint_registry.setdefault(
                        "twist", {})[short] = new_joint

        cmds.delete(new_root)

    @staticmethod
    def build_twist_deform_drivers():

        schema = UE5_SCHEMA.get("twist", {})

        twist_map = RIG_CTX.joint_registry.get("twist", {})
        deform_map = RIG_CTX.joint_registry.get("deform", {})

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                driver_short = chain[0]
                twist01_short = chain[1]
                twist02_short = chain[2]

                driver = deform_map.get(driver_short)
                twist01 = twist_map.get(twist01_short)
                twist02 = twist_map.get(twist02_short)

                initial_rx = cmds.getAttr(driver + ".rotateX")

                pma = cmds.createNode("plusMinusAverage",
                                      n=f"{driver_short}_twistDelta_PMA")
                cmds.setAttr(pma + ".operation", 2)
                cmds.setAttr(pma + ".input1D[1]", initial_rx)
                cmds.connectAttr(driver + ".rotateX",
                                 pma + ".input1D[0]", force=True)

                md01 = cmds.createNode("multiplyDivide",
                                       n=f"{twist01_short}_twist_MD")
                md02 = cmds.createNode("multiplyDivide",
                                       n=f"{twist02_short}_twist_MD")
                cmds.setAttr(md01 + ".input2X", 0.33)
                cmds.setAttr(md02 + ".input2X", 0.66)

                cmds.connectAttr(pma + ".output1D",
                                 md01 + ".input1X", force=True)
                cmds.connectAttr(md01 + ".outputX",
                                 twist01 + ".rotateX", force=True)

                cmds.connectAttr(pma + ".output1D",
                                 md02 + ".input1X", force=True)
                cmds.connectAttr(md02 + ".outputX",
                                 twist02 + ".rotateX", force=True)

                twist_root_joint = twist_map.get(f"{limb_name}_{side}")
                driver_joint = deform_map.get(driver_short)
                limb_root_joint = deform_map.get(f"{limb_name}_{side}")
                twist_limb_grp = RIG_CTX.joint_registry.get(
                    "twist_groups", {}).get(f"{limb_name}_{side}")
                cmds.parentConstraint(
                    limb_root_joint, twist_limb_grp, mo=False)

                aim_locator = cmds.spaceLocator(
                    n=f"{limb_name}_{side}_twistAim_LOC")[0]
                cmds.parent(aim_locator, twist_limb_grp)
                cmds.matchTransform(aim_locator, twist_root_joint)
                aim_locator = cmds.ls(
                    f"{limb_name}_{side}_twistAim_LOC", long=True, )[0]

                driver_pos = cmds.xform(driver_joint, q=True, ws=True, t=True)
                root_pos = cmds.xform(
                    twist_root_joint, q=True, ws=True, t=True)
                m = cmds.xform(twist_root_joint, q=True, ws=True, m=True)
                root_x_axis = [m[0], m[1], m[2]]
                vec = [driver_pos[0] - root_pos[0],
                       driver_pos[1] - root_pos[1],
                       driver_pos[2] - root_pos[2],]
                dot = (root_x_axis[0] * vec[0] +
                       root_x_axis[1] * vec[1] +
                       root_x_axis[2] * vec[2])
                aim_x = 1 if dot >= 0 else -1

                cmds.aimConstraint(
                    driver_joint, twist_root_joint,
                    aimVector=(aim_x, 0, 0), upVector=(0, 1, 0),
                    worldUpType="object", worldUpObject=aim_locator, mo=False)

                twist01_deform = deform_map[twist01_short]
                twist02_deform = deform_map[twist02_short]
                cmds.parentConstraint(twist01, twist01_deform, mo=False)
                cmds.parentConstraint(twist02, twist02_deform, mo=False)

    @staticmethod
    def build_neck_skeleton(root):

        RigHelpers.build_schema_skeleton(root, "neck", "fk")

    @staticmethod
    def build_neck_FK_controls(root):

        rig_root = RigHelpers.get_or_create_rig_root()
        controls_grp = RigHelpers.get_or_create_child(rig_root, "controls")
        main_system = RigHelpers.get_or_create_child(
            controls_grp, "MainSystem")
        fk_system = RigHelpers.get_or_create_child(controls_grp, "FKSystem")

        main_system = cmds.ls(main_system, long=True)[0]
        fk_system = cmds.ls(fk_system, long=True)[0]

        all_joints = [root]+cmds.listRelatives(
            root, ad=True, type="joint", fullPath=True) or []
        joint_map = {j.split("|")[-1]: j for j in all_joints}

        RigHelpers.build_fk_chain_controls(category="neck", joint_map=joint_map,
                                           parent_grp=fk_system, size="medium")

    @staticmethod
    def build_clavicle_skeleton(root):

        RigHelpers.build_schema_skeleton(root, "clavicle", "fk")

    @staticmethod
    def build_clavicle_fk_joint_drivers():

        clavicle_schema = UE5_SCHEMA.get("clavicle", {})

        rig_root = RigHelpers.get_or_create_rig_root()
        controls_grp = RigHelpers.get_or_create_child(rig_root, "controls")
        fk_system = RigHelpers.get_or_create_child(controls_grp, "FKSystem")
        fk_system = cmds.ls(fk_system, long=True)[0]

        fk_ctrl_map = RIG_CTX.control_registry.get("fk", {})
        fk_joint_map = RIG_CTX.joint_registry.get("fk", {})
        deform_map = RIG_CTX.joint_registry.get("deform", {})

        for side, side_dict in clavicle_schema.items():

            side_grp = cmds.group(
                em=True, n=f"fk_clavicle_{side}_GRP", p=fk_system)
            side_grp = cmds.ls(side_grp, long=True)[0]
            RIG_CTX.control_registry.setdefault(
                "fk_groups", {})[f"clavicle_{side}"] = side_grp

            for limb_name, chain in side_dict.items():

                limb_grp = cmds.group(
                    em=True, n=f"fk_{limb_name}_{side}_GRP", p=side_grp)
                limb_grp = cmds.ls(limb_grp, long=True)[0]
                RIG_CTX.control_registry.setdefault(
                    "fk_groups", {})[f"{limb_name}_{side}"] = limb_grp

                for joint_name in chain:

                    fk_joint = fk_joint_map.get(joint_name)
                    deform_joint = deform_map.get(joint_name)

                    ctrl = CtrlFactory.create_ctrl_half_circle_ribbon(
                        name=f"{joint_name}_fk_CTRL", size="medium",
                        thickness=0.2, segments=20, color_index=17)
                    if side == "l":
                        cmds.rotate(-180, 0, 0, ctrl, r=True, os=True)
                    cmds.makeIdentity(ctrl, apply=True, t=1, r=1, s=1, n=0)
                    cmds.matchTransform(ctrl, deform_joint)

                    ctrl = cmds.parent(ctrl, limb_grp)[0]
                    ctrl = cmds.ls(ctrl, long=True)[0]
                    RIG_CTX.control_registry.setdefault(
                        "fk", {})[joint_name] = ctrl
                    RigHelpers.freeze_to_offset_parent_matrix(ctrl)

                    cmds.connectAttr(
                        f"{ctrl}.translate",
                        f"{fk_joint}.translate", force=True)
                    cmds.connectAttr(
                        f"{ctrl}.rotate",
                        f"{fk_joint}.rotate", force=True)
                    cmds.parentConstraint(fk_joint, deform_joint, mo=False)

    @staticmethod
    def connect_limb_follow_clavicle():

        clavicle_schema = UE5_SCHEMA.get("clavicle", {})

        fk_ctrl_map = RIG_CTX.control_registry.get("fk", {})

        fk_ctrl_group_map = RIG_CTX.control_registry.get("fk_groups", {})
        fk_joint_group_map = RIG_CTX.joint_registry.get("fk_groups", {})

        ik_joint_group_map = RIG_CTX.joint_registry.get("ik_groups", {})

        for side, side_dict in clavicle_schema.items():
            for limb_name, chain in side_dict.items():

                clavicle_name = chain[0]

                clavicle_fk_ctrl = fk_ctrl_map.get(clavicle_name)

                fk_follow_grp = cmds.group(
                    em=True, n=f"fk_clavicle_{side}_follow_GRP")
                fk_follow_grp = cmds.parent(fk_follow_grp, clavicle_fk_ctrl)[0]
                fk_follow_grp = cmds.ls(fk_follow_grp, l=True)[0]

                upperarm_follow_targets = []
                upperarm_follow_targets.extend([
                    fk_ctrl_group_map.get(f"upperarm_{side}"),
                    fk_joint_group_map.get(f"upperarm_{side}"),
                    ik_joint_group_map.get(f"upperarm_{side}")])

                for node in upperarm_follow_targets:
                    cmds.connectAttr(
                        f"{fk_follow_grp}.worldMatrix[0]",
                        f"{node}.offsetParentMatrix", force=True)

    @staticmethod
    def connect_clavicle_follow_spine():

        fk_ctrl_map = RIG_CTX.control_registry.get("fk", {})
        ik_ctrl_map = RIG_CTX.control_registry.get("ik", {})

        ik_joint_map = RIG_CTX.joint_registry.get("ik", {})

        fk_ctrl_group_map = RIG_CTX.control_registry.get("fk_groups", {})
        fk_joint_group_map = RIG_CTX.joint_registry.get("fk_groups", {})

        spine_chain = UE5_SCHEMA["spine"]["c"]["spine"]
        spine_fk_ctrl = fk_ctrl_map[spine_chain[-2]]
        spine_ik_joint = ik_joint_map[spine_chain[-1]]
        spine_ikfk_ctrl = RIG_CTX.control_registry["ikfk"][spine_chain[0]]

        fk_follow_grp = cmds.group(em=True, n="fk_spine_follow_GRP")
        fk_follow_grp = cmds.parent(fk_follow_grp, spine_fk_ctrl)[0]
        fk_follow_grp = cmds.ls(fk_follow_grp, l=True)[0]

        ik_follow_grp = cmds.group(em=True, n="ik_spine_follow_GRP")
        ik_follow_grp = cmds.parent(ik_follow_grp, spine_ik_joint)[0]
        ik_follow_grp = cmds.ls(ik_follow_grp, l=True)[0]

        clavicle_follow_targets = []

        for side in ("l", "r"):
            clavicle_follow_targets.extend([
                fk_ctrl_group_map.get(f"clavicle_{side}"),
                fk_joint_group_map.get(f"clavicle_{side}"),])

        blend_node = cmds.createNode("blendMatrix", n="spine_follow_BM")
        cmds.connectAttr(
            f"{ik_follow_grp}.worldMatrix[0]",
            f"{blend_node}.inputMatrix", force=True)
        cmds.connectAttr(
            f"{fk_follow_grp}.worldMatrix[0]",
            f"{blend_node}.target[0].targetMatrix", force=True)

        md = cmds.createNode("multiplyDivide", n="spine_follow_weight_MD")
        cmds.setAttr(md + ".input2X", 0.1)
        cmds.connectAttr(
            f"{spine_ikfk_ctrl}.IKFKBlend", md + ".input1X", force=True)
        cmds.connectAttr(md + ".outputX", f"{blend_node}.envelope", force=True)

        for node in clavicle_follow_targets:
            cmds.connectAttr(
                f"{blend_node}.outputMatrix",
                f"{node}.offsetParentMatrix", force=True)

    @staticmethod
    def build_spine_squash_stretch_drivers():

        rig_root = RigHelpers.get_or_create_rig_root()
        driving_root = RigHelpers.get_or_create_child(
            rig_root, "driving_system")
        curves = cmds.listRelatives(
            driving_root, type="nurbsCurve", ad=True, fullPath=True)[0] or []

        curve_info = cmds.createNode("curveInfo", n="spine_squashStretch_CI")
        cmds.connectAttr(curves + ".worldSpace[0]",
                         curve_info + ".inputCurve", force=True)
        original_length = cmds.getAttr(curve_info + ".arcLength")

        md = cmds.createNode(
            "multiplyDivide", n="spine_squashStretch_ratio_MD")
        cmds.setAttr(md + ".operation", 2)
        cmds.setAttr(md + ".input2X", original_length)
        cmds.connectAttr(curve_info + ".arcLength",
                         md + ".input1X", force=True)

        end_ctrl = RIG_CTX.control_registry["ik"].get("spine_end_follow")
        stretch_md = cmds.createNode(
            "multiplyDivide", n="spine_stretchy_normalize_MD")
        cmds.setAttr(stretch_md + ".input2X", 0.1)
        cmds.connectAttr(end_ctrl + ".Stretchy",
                         stretch_md + ".input1X", force=True)

        blend = cmds.createNode("blendColors", n="spine_squashStretch_BC")
        cmds.setAttr(blend + ".color1R", 1)
        cmds.setAttr(blend + ".color2R", 1)
        cmds.connectAttr(stretch_md + ".outputX",
                         blend + ".blender", force=True)
        cmds.connectAttr(md + ".outputX",
                         blend + ".color1R", force=True)

        cond = cmds.createNode("condition", n="spine_squashStretch_COND")
        cmds.setAttr(cond + ".operation", 1)
        cmds.setAttr(cond + ".secondTerm", 1)
        cmds.setAttr(cond + ".colorIfFalseR", 1)
        cmds.connectAttr(md + ".outputX",
                         cond + ".firstTerm", force=True)

        cmds.connectAttr(blend + ".outputR",
                         cond + ".colorIfTrueR", force=True)

        ikfk_ctrl = RIG_CTX.control_registry[
            "ikfk"].get(UE5_SCHEMA["spine"]["c"]["spine"][0])
        ikfk_md = cmds.createNode(
            "multiplyDivide", n="spine_ikfk_normalize_MD")
        cmds.setAttr(ikfk_md + ".input2X", 0.1)
        cmds.connectAttr(ikfk_ctrl + ".IKFKBlend",
                         ikfk_md + ".input1X", force=True)

        ikfk_blend = cmds.createNode(
            "blendColors", n="spine_squashStretch_IKFK_BC")
        cmds.setAttr(ikfk_blend + ".color1R", 1)
        cmds.setAttr(ikfk_blend + ".color1G", 1)
        cmds.connectAttr(ikfk_md + ".outputX",
                         ikfk_blend + ".blender", force=True)
        cmds.connectAttr(cond + ".outColorR",
                         ikfk_blend + ".color2R", force=True)

        volume_md = cmds.createNode("multiplyDivide",
                                    n="spine_volume_MD")
        cmds.setAttr(volume_md + ".operation", 3)
        cmds.setAttr(volume_md + ".input2X", -0.5)
        cmds.connectAttr(cond + ".outColorR",
                         volume_md + ".input1X", force=True)

        cmds.connectAttr(volume_md + ".outputX",
                         ikfk_blend + ".color2G", force=True)

        spine_chain = UE5_SCHEMA["spine"]["c"]["spine"]
        ik_joint_map = RIG_CTX.joint_registry.get("ik", {})
        deform_joint_map = RIG_CTX.joint_registry.get("deform", {})

        for joint_name in spine_chain[:-2]:
            ik_joint = ik_joint_map.get(joint_name)
            cmds.connectAttr(ikfk_blend + ".outputR",
                             ik_joint + ".scaleX", force=True)
            cmds.connectAttr(ikfk_blend + ".outputG",
                             ik_joint + ".scaleY", force=True)
            cmds.connectAttr(ikfk_blend + ".outputG",
                             ik_joint + ".scaleZ", force=True)

        for joint_name in spine_chain[:-2]:
            ik_joint = ik_joint_map.get(joint_name)
            deform_joint = deform_joint_map.get(joint_name)
            cmds.connectAttr(ik_joint + ".scale",
                             deform_joint + ".scale", force=True)

        for joint_name in spine_chain:
            ik_joint = ik_joint_map.get(joint_name)
            deform_joint = deform_joint_map.get(joint_name)
            cmds.setAttr(ik_joint + ".segmentScaleCompensate", 1)
            cmds.setAttr(deform_joint + ".segmentScaleCompensate", 1)

    @staticmethod
    def build_spine_squash_mid_delta_correction():

        start_jnt = cmds.ls("spine_start_follow_JNT", type="joint")[0]
        end_jnt = cmds.ls("spine_end_follow_JNT", type="joint")[0]
        mid_jnt = cmds.ls("spine_mid_follow_JNT", type="joint")[0]

        start_ws = cmds.xform(start_jnt, q=True, ws=True, t=True)
        end_ws = cmds.xform(end_jnt, q=True, ws=True, t=True)

        original_mid = [
            (start_ws[0] + end_ws[0]) * 0.5,
            (start_ws[1] + end_ws[1]) * 0.5,
            (start_ws[2] + end_ws[2]) * 0.5,]

        start_dcm = cmds.createNode("decomposeMatrix", n="spine_start_DCM")
        end_dcm = cmds.createNode("decomposeMatrix", n="spine_end_DCM")

        cmds.connectAttr(start_jnt + ".worldMatrix[0]",
                         start_dcm + ".inputMatrix", f=True)
        cmds.connectAttr(end_jnt + ".worldMatrix[0]",
                         end_dcm + ".inputMatrix", f=True)

        pma = cmds.createNode("plusMinusAverage", n="spine_mid_add_PMA")
        cmds.setAttr(pma + ".operation", 1)

        cmds.connectAttr(start_dcm + ".outputTranslate",
                         pma + ".input3D[0]", f=True)
        cmds.connectAttr(end_dcm + ".outputTranslate",
                         pma + ".input3D[1]", f=True)

        md = cmds.createNode("multiplyDivide", n="spine_mid_half_MD")
        cmds.setAttr(md + ".input2X", 0.5)
        cmds.setAttr(md + ".input2Y", 0.5)
        cmds.setAttr(md + ".input2Z", 0.5)

        cmds.connectAttr(pma + ".output3D",
                         md + ".input1", f=True)

        delta_pma = cmds.createNode(
            "plusMinusAverage", n="spine_mid_delta_PMA")
        cmds.setAttr(delta_pma + ".operation", 2)

        cmds.connectAttr(md + ".output",
                         delta_pma + ".input3D[0]", f=True)

        cmds.setAttr(delta_pma + ".input3D[1]",
                     original_mid[0],
                     original_mid[1],
                     original_mid[2],
                     type="double3")

        cm = cmds.createNode("composeMatrix", n="spine_mid_CM")
        cmds.connectAttr(delta_pma + ".output3D",
                         cm + ".inputTranslate", f=True)

        mid_ctrl = cmds.ls("spine_mid_follow_CTRL", long=True)[0]
        original_ctrl_opm = cmds.getAttr(mid_ctrl + ".offsetParentMatrix")
        mm = cmds.createNode("multMatrix", n="spine_mid_MM")
        cmds.setAttr(mm + ".matrixIn[0]", *original_ctrl_opm, type="matrix")
        cmds.connectAttr(cm + ".outputMatrix",
                         mm + ".matrixIn[1]", f=True)
        cmds.connectAttr(mm + ".matrixSum",
                         mid_ctrl + ".offsetParentMatrix", f=True)

        original_joint_opm = cmds.getAttr(mid_jnt + ".offsetParentMatrix")
        joint_mm = cmds.createNode("multMatrix", n="spine_mid_joint_MM")
        cmds.setAttr(joint_mm + ".matrixIn[0]",
                     *original_joint_opm, type="matrix")
        cmds.connectAttr(cm + ".outputMatrix",
                         joint_mm + ".matrixIn[1]", f=True)
        cmds.connectAttr(joint_mm + ".matrixSum",
                         mid_jnt + ".offsetParentMatrix", f=True)

    @staticmethod
    def build_arm_squash_stretch_drivers():

        limb_schema = UE5_SCHEMA.get("limb", {})
        deform_joint_map = RIG_CTX.joint_registry.get("deform", {})
        ik_joint_map = RIG_CTX.joint_registry.get("ik", {})
        ik_ctrl_map = RIG_CTX.control_registry.get("ik", {})

        rig_root = RigHelpers.get_or_create_rig_root()
        driving_root = RigHelpers.get_or_create_child(
            rig_root, "driving_system")
        arm_stretch_root = RigHelpers.get_or_create_child(
            driving_root, "arm_stretch_system")
        arm_stretch_root = cmds.ls(arm_stretch_root, long=True)[0]

        for side, side_dict in limb_schema.items():
            arm_chain = side_dict.get("upperarm")

            start_name = arm_chain[0]
            mid_name = arm_chain[1]
            end_name = arm_chain[2]

            start_joint = deform_joint_map.get(start_name)
            mid_joint = deform_joint_map.get(mid_name)
            end_joint = deform_joint_map.get(end_name)

            start_loc = cmds.spaceLocator(n=f"{start_name}_stretch_LOC")[0]
            mid_loc = cmds.spaceLocator(n=f"{mid_name}_stretch_LOC")[0]
            end_loc = cmds.spaceLocator(n=f"{end_name}_stretch_LOC")[0]

            cmds.matchTransform(start_loc, start_joint)
            cmds.matchTransform(mid_loc, mid_joint)
            cmds.matchTransform(end_loc, end_joint)

            ik_ctrl = ik_ctrl_map.get(end_name)

            cmds.parent(start_loc, arm_stretch_root)
            cmds.parent(mid_loc, arm_stretch_root)
            cmds.parent(end_loc, ik_ctrl)

            start_loc = cmds.ls(start_loc, long=True)[0]
            mid_loc = cmds.ls(mid_loc, long=True)[0]
            end_loc = cmds.ls(end_loc, long=True)[0]

            upper_dist = cmds.createNode("distanceBetween",
                                         n=f"{start_name}_to_{mid_name}_DIST")
            lower_dist = cmds.createNode("distanceBetween",
                                         n=f"{mid_name}_to_{end_name}_DIST")

            cmds.connectAttr(f"{start_loc}.worldMatrix[0]",
                             f"{upper_dist}.inMatrix1", force=True)
            cmds.connectAttr(f"{mid_loc}.worldMatrix[0]",
                             f"{upper_dist}.inMatrix2", force=True)
            cmds.connectAttr(f"{mid_loc}.worldMatrix[0]",
                             f"{lower_dist}.inMatrix1", force=True)
            cmds.connectAttr(f"{end_loc}.worldMatrix[0]",
                             f"{lower_dist}.inMatrix2", force=True)

            total_len = cmds.createNode("plusMinusAverage",
                                        n=f"{start_name}_armLength_PMA")
            cmds.setAttr(total_len + ".operation", 1)
            cmds.connectAttr(upper_dist + ".distance",
                             total_len + ".input1D[0]", f=True)
            cmds.connectAttr(lower_dist + ".distance",
                             total_len + ".input1D[1]", f=True)

            original_length = cmds.getAttr(total_len + ".output1D")
            cmds.delete(mid_loc)

            current_dist = cmds.createNode("distanceBetween",
                                           n=f"{start_name}_armCurrent_DIST")
            cmds.connectAttr(f"{start_loc}.worldMatrix[0]",
                             f"{current_dist}.inMatrix1", force=True)
            cmds.connectAttr(f"{end_loc}.worldMatrix[0]",
                             f"{current_dist}.inMatrix2", force=True)

            md = cmds.createNode(
                "multiplyDivide", n=f"{start_name}_stretch_ratio_MD")
            cmds.setAttr(md + ".operation", 2)
            cmds.setAttr(md + ".input2X", original_length)
            cmds.connectAttr(current_dist + ".distance",
                             md + ".input1X", force=True)

            end_ctrl = ik_ctrl_map.get(end_name)
            stretch_md = cmds.createNode(
                "multiplyDivide", n=f"{start_name}_stretch_normalize_MD")
            cmds.setAttr(stretch_md + ".input2X", 0.1)
            cmds.connectAttr(end_ctrl + ".Stretchy",
                             stretch_md + ".input1X", force=True)

            blend = cmds.createNode(
                "blendColors", n=f"{start_name}_stretch_BC")
            cmds.setAttr(blend + ".color1R", 1)
            cmds.setAttr(blend + ".color2R", 1)
            cmds.connectAttr(stretch_md + ".outputX",
                             blend + ".blender", force=True)
            cmds.connectAttr(md + ".outputX",
                             blend + ".color1R", force=True)

            cond = cmds.createNode("condition", n=f"{start_name}_stretch_COND")
            cmds.setAttr(cond + ".operation", 2)
            cmds.setAttr(cond + ".secondTerm", 1)
            cmds.setAttr(cond + ".colorIfFalseR", 1)
            cmds.connectAttr(md + ".outputX",
                             cond + ".firstTerm", force=True)

            cmds.connectAttr(blend + ".outputR",
                             cond + ".colorIfTrueR", force=True)

            ikfk_ctrl = RIG_CTX.control_registry["ikfk"].get(start_name)
            ikfk_md = cmds.createNode("multiplyDivide",
                                      n=f"{start_name}_ikfk_normalize_MD")
            cmds.setAttr(ikfk_md + ".input2X", 0.1)
            cmds.connectAttr(ikfk_ctrl + ".IKFKBlend",
                             ikfk_md + ".input1X", force=True)

            ikfk_blend = cmds.createNode(
                "blendColors", n=f"{start_name}_ikfk_BC")
            cmds.setAttr(ikfk_blend + ".color1R", 1)
            cmds.setAttr(ikfk_blend + ".color1G", 1)
            cmds.connectAttr(ikfk_md + ".outputX",
                             ikfk_blend + ".blender", force=True)
            cmds.connectAttr(cond + ".outColorR",
                             ikfk_blend + ".color2R", force=True)

            volume_md = cmds.createNode("multiplyDivide",
                                        n=f"{start_name}_volume_MD")
            cmds.setAttr(volume_md + ".operation", 3)
            cmds.setAttr(volume_md + ".input2X", -0.5)
            cmds.connectAttr(cond + ".outColorR",
                             volume_md + ".input1X", force=True)

            cmds.connectAttr(volume_md + ".outputX",
                             ikfk_blend + ".color2G", force=True)

            for joint_name in arm_chain[:-1]:
                ik_joint = ik_joint_map.get(joint_name)
                cmds.connectAttr(ikfk_blend + ".outputR",
                                 ik_joint + ".scaleX", force=True)
                cmds.connectAttr(ikfk_blend + ".outputG",
                                 ik_joint + ".scaleY", force=True)
                cmds.connectAttr(ikfk_blend + ".outputG",
                                 ik_joint + ".scaleZ", force=True)

            for joint_name in arm_chain[:-1]:
                ik_joint = ik_joint_map.get(joint_name)
                deform_joint = deform_joint_map.get(joint_name)
                cmds.connectAttr(ik_joint + ".scale",
                                 deform_joint + ".scale", force=True)

            for joint_name in arm_chain:
                ik_joint = ik_joint_map.get(joint_name)
                deform_joint = deform_joint_map.get(joint_name)
                cmds.setAttr(ik_joint + ".segmentScaleCompensate", 1)
                cmds.setAttr(deform_joint + ".segmentScaleCompensate", 1)

            twist_map = RIG_CTX.joint_registry.get("twist", {})
            limb_name, side = start_name.rsplit("_", 1)
            for limb_name in ("upperarm", "lowerarm"):
                twist_first_name = f"{limb_name}_{side}"
                twist_first = twist_map.get(twist_first_name)
                deform_joint = deform_joint_map.get(twist_first_name)
                cmds.connectAttr(ikfk_blend + ".outputR",
                                 twist_first + ".scaleX", force=True)
                cmds.connectAttr(ikfk_blend + ".outputG",
                                 twist_first + ".scaleY", force=True)
                cmds.connectAttr(ikfk_blend + ".outputG",
                                 twist_first + ".scaleZ", force=True)

                cmds.connectAttr(twist_first + ".scale",
                                 deform_joint + ".scale", force=True)
                cmds.setAttr(twist_first + ".segmentScaleCompensate", 1)
                cmds.setAttr(deform_joint + ".segmentScaleCompensate", 1)

    @staticmethod
    def build_leg_squash_stretch_drivers():

        limb_schema = UE5_SCHEMA.get("limb", {})
        deform_joint_map = RIG_CTX.joint_registry.get("deform", {})
        ik_joint_map = RIG_CTX.joint_registry.get("ik", {})
        ik_ctrl_map = RIG_CTX.control_registry.get("ik", {})

        rig_root = RigHelpers.get_or_create_rig_root()
        driving_root = RigHelpers.get_or_create_child(
            rig_root, "driving_system")
        arm_stretch_root = RigHelpers.get_or_create_child(
            driving_root, "arm_stretch_system")
        arm_stretch_root = cmds.ls(arm_stretch_root, long=True)[0]

        for side, side_dict in limb_schema.items():
            arm_chain = side_dict.get("thigh")

            start_name = arm_chain[0]
            mid_name = arm_chain[1]
            end_name = arm_chain[2]

            start_joint = deform_joint_map.get(start_name)
            mid_joint = deform_joint_map.get(mid_name)
            end_joint = deform_joint_map.get(end_name)

            start_loc = cmds.spaceLocator(n=f"{start_name}_stretch_LOC")[0]
            mid_loc = cmds.spaceLocator(n=f"{mid_name}_stretch_LOC")[0]
            end_loc = cmds.spaceLocator(n=f"{end_name}_stretch_LOC")[0]

            cmds.matchTransform(start_loc, start_joint)
            cmds.matchTransform(mid_loc, mid_joint)
            cmds.matchTransform(end_loc, end_joint)

            ik_ctrl = ik_ctrl_map.get(end_name)

            cmds.parent(start_loc, arm_stretch_root)
            cmds.parent(mid_loc, arm_stretch_root)
            cmds.parent(end_loc, ik_ctrl)

            start_loc = cmds.ls(start_loc, long=True)[0]
            mid_loc = cmds.ls(mid_loc, long=True)[0]
            end_loc = cmds.ls(end_loc, long=True)[0]

            upper_dist = cmds.createNode("distanceBetween",
                                         n=f"{start_name}_to_{mid_name}_DIST")
            lower_dist = cmds.createNode("distanceBetween",
                                         n=f"{mid_name}_to_{end_name}_DIST")

            cmds.connectAttr(f"{start_loc}.worldMatrix[0]",
                             f"{upper_dist}.inMatrix1", force=True)
            cmds.connectAttr(f"{mid_loc}.worldMatrix[0]",
                             f"{upper_dist}.inMatrix2", force=True)
            cmds.connectAttr(f"{mid_loc}.worldMatrix[0]",
                             f"{lower_dist}.inMatrix1", force=True)
            cmds.connectAttr(f"{end_loc}.worldMatrix[0]",
                             f"{lower_dist}.inMatrix2", force=True)

            total_len = cmds.createNode("plusMinusAverage",
                                        n=f"{start_name}_armLength_PMA")
            cmds.setAttr(total_len + ".operation", 1)
            cmds.connectAttr(upper_dist + ".distance",
                             total_len + ".input1D[0]", f=True)
            cmds.connectAttr(lower_dist + ".distance",
                             total_len + ".input1D[1]", f=True)

            original_length = cmds.getAttr(total_len + ".output1D")
            cmds.delete(mid_loc)

            current_dist = cmds.createNode("distanceBetween",
                                           n=f"{start_name}_armCurrent_DIST")
            cmds.connectAttr(f"{start_loc}.worldMatrix[0]",
                             f"{current_dist}.inMatrix1", force=True)
            cmds.connectAttr(f"{end_loc}.worldMatrix[0]",
                             f"{current_dist}.inMatrix2", force=True)

            md = cmds.createNode(
                "multiplyDivide", n=f"{start_name}_stretch_ratio_MD")
            cmds.setAttr(md + ".operation", 2)
            cmds.setAttr(md + ".input2X", original_length)
            cmds.connectAttr(current_dist + ".distance",
                             md + ".input1X", force=True)

            end_ctrl = ik_ctrl_map.get(end_name)
            stretch_md = cmds.createNode(
                "multiplyDivide", n=f"{start_name}_stretch_normalize_MD")
            cmds.setAttr(stretch_md + ".input2X", 0.1)
            cmds.connectAttr(end_ctrl + ".Stretchy",
                             stretch_md + ".input1X", force=True)

            blend = cmds.createNode(
                "blendColors", n=f"{start_name}_stretch_BC")
            cmds.setAttr(blend + ".color1R", 1)
            cmds.setAttr(blend + ".color2R", 1)
            cmds.connectAttr(stretch_md + ".outputX",
                             blend + ".blender", force=True)
            cmds.connectAttr(md + ".outputX",
                             blend + ".color1R", force=True)

            cond = cmds.createNode("condition", n=f"{start_name}_stretch_COND")
            cmds.setAttr(cond + ".operation", 2)
            cmds.setAttr(cond + ".secondTerm", 1)
            cmds.setAttr(cond + ".colorIfFalseR", 1)
            cmds.connectAttr(md + ".outputX",
                             cond + ".firstTerm", force=True)

            cmds.connectAttr(blend + ".outputR",
                             cond + ".colorIfTrueR", force=True)

            ikfk_ctrl = RIG_CTX.control_registry["ikfk"].get(start_name)
            ikfk_md = cmds.createNode("multiplyDivide",
                                      n=f"{start_name}_ikfk_normalize_MD")
            cmds.setAttr(ikfk_md + ".input2X", 0.1)
            cmds.connectAttr(ikfk_ctrl + ".IKFKBlend",
                             ikfk_md + ".input1X", force=True)

            ikfk_blend = cmds.createNode(
                "blendColors", n=f"{start_name}_ikfk_BC")
            cmds.setAttr(ikfk_blend + ".color1R", 1)
            cmds.setAttr(ikfk_blend + ".color1G", 1)
            cmds.connectAttr(ikfk_md + ".outputX",
                             ikfk_blend + ".blender", force=True)
            cmds.connectAttr(cond + ".outColorR",
                             ikfk_blend + ".color2R", force=True)

            volume_md = cmds.createNode("multiplyDivide",
                                        n=f"{start_name}_volume_MD")
            cmds.setAttr(volume_md + ".operation", 3)
            cmds.setAttr(volume_md + ".input2X", -0.5)
            cmds.connectAttr(cond + ".outColorR",
                             volume_md + ".input1X", force=True)

            cmds.connectAttr(volume_md + ".outputX",
                             ikfk_blend + ".color2G", force=True)

            for joint_name in arm_chain[:-1]:
                ik_joint = ik_joint_map.get(joint_name)
                cmds.connectAttr(ikfk_blend + ".outputR",
                                 ik_joint + ".scaleX", force=True)
                cmds.connectAttr(ikfk_blend + ".outputG",
                                 ik_joint + ".scaleY", force=True)
                cmds.connectAttr(ikfk_blend + ".outputG",
                                 ik_joint + ".scaleZ", force=True)

            for joint_name in arm_chain[:-1]:
                ik_joint = ik_joint_map.get(joint_name)
                deform_joint = deform_joint_map.get(joint_name)
                cmds.connectAttr(ik_joint + ".scale",
                                 deform_joint + ".scale", force=True)

            for joint_name in arm_chain:
                ik_joint = ik_joint_map.get(joint_name)
                deform_joint = deform_joint_map.get(joint_name)
                cmds.setAttr(ik_joint + ".segmentScaleCompensate", 1)
                cmds.setAttr(deform_joint + ".segmentScaleCompensate", 1)

            twist_map = RIG_CTX.joint_registry.get("twist", {})
            limb_name, side = start_name.rsplit("_", 1)
            for limb_name in ("thigh", "calf"):
                twist_first_name = f"{limb_name}_{side}"
                twist_first = twist_map.get(twist_first_name)
                deform_joint = deform_joint_map.get(twist_first_name)
                cmds.connectAttr(ikfk_blend + ".outputR",
                                 twist_first + ".scaleX", force=True)
                cmds.connectAttr(ikfk_blend + ".outputG",
                                 twist_first + ".scaleY", force=True)
                cmds.connectAttr(ikfk_blend + ".outputG",
                                 twist_first + ".scaleZ", force=True)

                cmds.connectAttr(twist_first + ".scale",
                                 deform_joint + ".scale", force=True)
                cmds.setAttr(twist_first + ".segmentScaleCompensate", 1)
                cmds.setAttr(deform_joint + ".segmentScaleCompensate", 1)

    @staticmethod
    def build_hip_skeleton_control():

        deform_map = RIG_CTX.joint_registry.get("deform", {})
        pelvis = deform_map.get("pelvis")

        rig_root = RigHelpers.get_or_create_rig_root()

        skeleton_grp = RigHelpers.get_or_create_child(rig_root, "skeleton")
        fk_grp = RigHelpers.get_or_create_child(skeleton_grp, "fk_joints")

        controls_grp = RigHelpers.get_or_create_child(rig_root, "controls")
        main_system = RigHelpers.get_or_create_child(
            controls_grp, "MainSystem")
        main_system = cmds.ls(main_system, long=True)[0]

        cross = CtrlFactory.create_ctrl_cross_arrow(name="hip_cross_CTRL")
        cross = cmds.parent(cross, main_system)[0]
        cross = cmds.ls(cross, long=True)[0]
        cmds.matchTransform(cross, pelvis)
        cmds.rotate(0, 0, 90, cross, r=True, os=True)
        RigHelpers.freeze_to_offset_parent_matrix(cross)
        RIG_CTX.control_registry.setdefault("main", {})["hip_cross"] = cross

        ctrl = CtrlFactory.create_ctrl_hip(name="hip_CTRL")
        ctrl = cmds.parent(ctrl, cross)[0]
        ctrl = cmds.ls(ctrl, long=True)[0]
        cmds.matchTransform(ctrl, pelvis)
        cmds.move(0, 0, 30, ctrl, r=True, os=True)
        RigHelpers.freeze_to_offset_parent_matrix(ctrl)
        RIG_CTX.control_registry.setdefault("main", {})["hip"] = ctrl

        fk_joint = cmds.duplicate(
            pelvis, parentOnly=True, name="pelvis_fk_JNT")[0]
        cmds.parent(fk_joint, cross)
        fk_joint = cmds.ls(fk_joint, long=True)[0]
        cmds.setAttr(fk_joint + ".jointOrient", 0, 0, 0)
        cmds.matchTransform(fk_joint, pelvis)
        RigHelpers.freeze_to_offset_parent_matrix(fk_joint)
        RIG_CTX.joint_registry.setdefault("fk", {})["pelvis"] = fk_joint

    @staticmethod
    def build_hip_driver():

        fk_joints = RIG_CTX.joint_registry.get("fk", {})
        deform_joints = RIG_CTX.joint_registry.get("deform", {})
        main_ctrls = RIG_CTX.control_registry.get("main", {})

        fk_joint = fk_joints.get("pelvis")
        deform_joint = deform_joints.get("pelvis")
        hip_ctrl = main_ctrls.get("hip")
        hip_cross_ctrl = main_ctrls.get("hip_cross")

        cmds.connectAttr(f"{hip_ctrl}.translate",
                         f"{fk_joint}.translate", force=True)
        cmds.connectAttr(f"{hip_ctrl}.rotate",
                         f"{fk_joint}.rotate", force=True)

        cmds.parentConstraint(fk_joint, deform_joint, mo=False)

        hip_cross_follow_grp = cmds.group(em=True, n="hip_follow_GRP")
        hip_cross_follow_grp = cmds.parent(
            hip_cross_follow_grp, hip_cross_ctrl)[0]
        hip_cross_follow_grp = cmds.ls(hip_cross_follow_grp, long=True)[0]

        hip_ctrl_follow_grp = cmds.group(em=True, n="hipCtrl_follow_GRP")
        hip_ctrl_follow_grp = cmds.parent(
            hip_ctrl_follow_grp, hip_cross_ctrl)[0]
        hip_ctrl_follow_grp = cmds.ls(hip_ctrl_follow_grp, long=True)[0]
        cmds.matchTransform(hip_ctrl_follow_grp, deform_joint)

        cross_follow_targets = []
        ctrl_follow_targets = []

        spine_ik_grp = RIG_CTX.control_registry.get(
            "ik_groups", {}).get("spine_c")
        spine_driver_grp = RIG_CTX.joint_registry.get(
            "driver_groups", {}).get("spine_follow")
        spine_ik_joint_grp = RIG_CTX.joint_registry.get(
            "ik_groups", {}).get("spine_01")

        cross_follow_targets.extend(
            [spine_ik_grp, spine_driver_grp, spine_ik_joint_grp])

        ik_joint_groups = RIG_CTX.joint_registry.get("ik_groups", {})
        cross_follow_targets.extend([ik_joint_groups.get("thigh_l"),
                                     ik_joint_groups.get("thigh_r"),])

        fk_groups = RIG_CTX.control_registry.get("fk_groups", {})
        ctrl_follow_targets.extend([fk_groups.get("thigh_l"),
                                    fk_groups.get("thigh_r"),
                                    fk_groups.get("spine_c"),])
        fk_joint_groups = RIG_CTX.joint_registry.get("fk_groups", {})
        ctrl_follow_targets.extend([fk_joint_groups.get("thigh_l"),
                                    fk_joint_groups.get("thigh_r"),
                                    fk_joint_groups.get("spine_01"),])

        for target in cross_follow_targets:
            cmds.connectAttr(f"{hip_cross_follow_grp}.worldMatrix[0]",
                             f"{target}.offsetParentMatrix", force=True)
        for target in ctrl_follow_targets:
            cmds.connectAttr(f"{hip_ctrl}.rotate",
                             f"{target}.rotate", force=True)
            cmds.connectAttr(f"{hip_ctrl_follow_grp}.worldMatrix[0]",
                             f"{target}.offsetParentMatrix", force=True)

    @staticmethod
    def build_ue5_auto_rig(root):

        RIG_CTX.control_registry.clear()
        RIG_CTX.joint_registry.clear()

        root = _run_step(RigOps.register_deform_skeleton, root)

        _run_step(RigOps.build_limb_FK_controls, root)
        _run_step(RigOps.build_limb_IK_controls, root)
        _run_step(RigOps.build_ikfk_switch_controls, root)

        _run_step(RigOps.build_twist_skeleton, root)

        _run_step(RigOps.build_limb_ik_fk_skeletons, root)
        _run_step(RigOps.build_limb_ikfk_deform_drivers)

        _run_step(RigOps.build_limb_fk_joint_drivers)
        _run_step(RigOps.build_limb_ik_joint_drivers)

        _run_step(RigOps.build_spine_ik_fk_skeletons, root)
        _run_step(RigOps.build_spine_fk_joint_drivers, root)
        _run_step(RigOps.build_spine_ik_joint_drivers)
        _run_step(RigOps.build_spine_deform_drivers)

        _run_step(RigOps.build_hand_controls)
        _run_step(RigOps.build_hand_spread_attributes)
        _run_step(RigOps.build_hand_curl_attributes)
        _run_step(RigOps.connect_hand_to_finger_groups)

        _run_step(RigOps.build_pole_vector_space_blend)
        _run_step(RigOps.build_foot_roll_drivers)
        _run_step(RigOps.build_twist_deform_drivers)

        _run_step(RigOps.build_clavicle_skeleton, root)
        _run_step(RigOps.build_clavicle_fk_joint_drivers)
        _run_step(RigOps.connect_limb_follow_clavicle)

        _run_step(RigOps.connect_clavicle_follow_spine)
        _run_step(RigOps.build_spine_squash_stretch_drivers)
        _run_step(RigOps.build_spine_squash_mid_delta_correction)
        _run_step(RigOps.build_arm_squash_stretch_drivers)
        _run_step(RigOps.build_leg_squash_stretch_drivers)

        _run_step(RigOps.build_hip_skeleton_control)
        _run_step(RigOps.build_hip_driver)

        print("\n" + "=" * 60)
        print("AUTO RIG LITE UE5 BUILD SUCCESS")
        print("=" * 60 + "\n")


class RigHelpers:

    @staticmethod
    def build_schema_skeleton(root_joint, category, suffix):

        # print(f"#######################{category}_{suffix}#######################")

        schema = UE5_SCHEMA.get(category, {})

        deform_map = RIG_CTX.joint_registry.get("deform", {})

        new_root = cmds.duplicate(root_joint, rr=True)[0]
        new_root = cmds.ls(new_root, long=True)[0]

        rig_root_grp = RigHelpers.get_or_create_rig_root()
        skeleton_grp = RigHelpers.get_or_create_child(rig_root_grp, "skeleton")
        joints_grp = RigHelpers.get_or_create_child(
            skeleton_grp, f"{suffix}_joints")

        full_hierarchy = [new_root] + (
            cmds.listRelatives(new_root, ad=True, type="joint", f=True) or [])
        joint_by_short = {j.split("|")[-1]: j for j in full_hierarchy}

        for _, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                base_joint = joint_by_short.get(chain[0])

                chain_grp = cmds.group(em=True, name=f"{suffix}_{chain[0]}")
                chain_grp = cmds.parent(chain_grp, joints_grp)[0]
                chain_grp = cmds.ls(chain_grp, long=True)[0]
                RIG_CTX.joint_registry.setdefault(
                    f"{suffix}_groups", {})[chain[0]] = chain_grp
                if suffix == "fk" and chain[0].startswith(("thigh", "spine")):
                    pelvis = RIG_CTX.joint_registry.get(
                        "deform", {}).get("pelvis")
                    cmds.matchTransform(chain_grp, pelvis)
                    RigHelpers.freeze_to_offset_parent_matrix(chain_grp)
                cmds.parent(base_joint, chain_grp)

                # cmds.matchTransform(chain_grp, base_joint)
                # RigHelpers.freeze_to_offset_parent_matrix(chain_grp)

                chain_root = cmds.listRelatives(
                    chain_grp, c=True, type="joint", f=True)[0]
                chain_joints = [chain_root] + (
                    cmds.listRelatives(chain_root, ad=True, type="joint", f=True) or [])
                chain_joints.sort(key=lambda x: x.count("|"), reverse=True)

                keep_set = set(chain)
                rename_queue = []

                for joint in chain_joints:
                    short = joint.split("|")[-1]
                    if short in keep_set:
                        rename_queue.append((joint, short))
                    else:
                        cmds.delete(joint)

                rename_queue.sort(key=lambda x: x[0].count("|"), reverse=True)

                for joint, short in rename_queue:
                    cmds.rename(joint, f"{short}_{suffix}_JNT")

                for joint, short in reversed(rename_queue):
                    new_joint = cmds.ls(f"{short}_{suffix}_JNT", long=True)[0]
                    deform_joint = deform_map.get(short)
                    cmds.matchTransform(new_joint, deform_joint)
                    RigHelpers.freeze_to_offset_parent_matrix(new_joint)
                    cmds.setAttr(new_joint + ".jointOrient", 0, 0, 0)
                    cmds.setAttr(new_joint + ".visibility", 0)
                    RIG_CTX.joint_registry.setdefault(
                        suffix, {})[short] = new_joint

        cmds.delete(new_root)

    @staticmethod
    def create_joint(name, parent, match_target):

        jnt = cmds.joint(n=name)
        jnt = cmds.parent(jnt, parent)[0]
        jnt = cmds.ls(jnt, long=True)[0]

        cmds.matchTransform(jnt, match_target)

        RigHelpers.freeze_to_offset_parent_matrix(jnt)
        cmds.setAttr(jnt + ".jointOrient", 0, 0, 0)
        # cmds.setAttr(jnt + ".visibility", 0)

        cmds.select(clear=True)

        return jnt

    @staticmethod
    def build_fk_chain_controls(category, joint_map, parent_grp, size):

        # print(f"##########################{category}##########################")

        schema = UE5_SCHEMA.get(category, {})

        for side, side_dict in schema.items():

            side_grp = cmds.group(
                em=True, n=f"fk_{category}_{side}_GRP", p=parent_grp)
            side_grp = cmds.ls(side_grp, long=True)[0]
            RIG_CTX.control_registry.setdefault(
                "fk_groups", {})[f"{category}_{side}_GRP"] = side_grp

            for limb_name, chain in side_dict.items():

                limb_grp = cmds.group(
                    em=True, n=f"fk_{limb_name}_{side}_GRP", p=side_grp)
                limb_grp = cmds.ls(limb_grp, long=True)[0]
                RIG_CTX.control_registry.setdefault(
                    "fk_groups", {})[f"{limb_name}_{side}"] = limb_grp
                if limb_name in ("thigh", "spine"):
                    pelvis = RIG_CTX.joint_registry.get(
                        "deform", {}).get("pelvis")
                    cmds.matchTransform(limb_grp, pelvis)
                    RigHelpers.freeze_to_offset_parent_matrix(limb_grp)

                # root_joint = joint_map.get(chain[0])
                # cmds.matchTransform(limb_grp, root_joint)
                # RigHelpers.freeze_to_offset_parent_matrix(limb_grp)

                previous_ctrl = None

                for jnt_name in chain:

                    jnt = joint_map.get(jnt_name)

                    ctrl = CtrlFactory.create_ctrl_fk(
                        name=f"{jnt_name}_fk_CTRL", size=size, normal=(1, 0, 0))
                    cmds.matchTransform(ctrl, jnt)

                    if previous_ctrl:
                        cmds.parent(ctrl, previous_ctrl)
                    else:
                        cmds.parent(ctrl, limb_grp)

                    ctrl = cmds.ls(ctrl, long=True)[0]
                    RigHelpers.freeze_to_offset_parent_matrix(ctrl)
                    RIG_CTX.control_registry.setdefault(
                        "fk", {})[jnt_name] = ctrl

                    previous_ctrl = ctrl

    @staticmethod
    def get_or_create_rig_root():
        if cmds.objExists("RIG_ROOT"):
            return "RIG_ROOT"
        return cmds.group(em=True, n="RIG_ROOT")

    @staticmethod
    def get_or_create_child(parent, name):
        path = f"{parent}|{name}"
        if cmds.objExists(path):
            return path
        return cmds.group(em=True, n=name, p=parent)

    @staticmethod
    def freeze_to_offset_parent_matrix(node):

        m = cmds.xform(node, q=True, m=True, os=True)

        cmds.setAttr(node + ".offsetParentMatrix", *m, type="matrix")

        cmds.setAttr(node + ".translate", 0, 0, 0)
        cmds.setAttr(node + ".rotate", 0, 0, 0)
        cmds.setAttr(node + ".scale", 1, 1, 1)

    @staticmethod
    def bake_joint_to_attributes(joint):

        world_mtx = cmds.xform(joint, q=True, m=True, ws=True)

        cmds.setAttr(joint + ".offsetParentMatrix",
                     *([1, 0, 0, 0,
                        0, 1, 0, 0,
                        0, 0, 1, 0,
                        0, 0, 0, 1]), type="matrix")

        cmds.setAttr(joint + ".jointOrient", 0, 0, 0)

        cmds.xform(joint, m=world_mtx, ws=True)


def get_maya_window():
    ptr = omui.MQtUtil.mainWindow()
    return shiboken6.wrapInstance(int(ptr), QtWidgets.QWidget)


def show_square_ui():
    show_square_ui.instance = MySquareUI()
    show_square_ui.instance.show(dockable=True)
    return show_square_ui.instance


def _run_step(func, *args):
    try:
        return func(*args)
    except Exception:
        print(f"\n[FAILED] {func.__name__}")
        raise


RIG_CTX = RigBuildContext()

show_square_ui()
