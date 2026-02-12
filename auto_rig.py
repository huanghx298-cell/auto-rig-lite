from PySide6 import QtWidgets, QtCore
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import shiboken6
import os
import random

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
        self._add_button("AUTO RIG LITE (UE5)",
                         self.on_auto_rig_lite)

        self.layout.addStretch()

    def on_debug(self):
        cmds.undoInfo(openChunk=True)
        try:
            ctrl = RigOps.create_ctrl_half_circle()
            cmds.select(ctrl, r=True)
        except Exception as e:
            cmds.warning(str(e))
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_auto_rig_lite(self):
        cmds.undoInfo(openChunk=True)
        try:
            sel = cmds.ls(sl=True, type="joint", long=True)
            if not sel:
                raise RuntimeError("Please select skeleton root joint")

            RigOps.auto_rig_lite_ue5(sel[0])
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
            "spine": ("spine_01", "spine_02", "spine_03", "spine_04", "spine_05",)
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

    "limb": {
        "l": {
            "upperarm": ("upperarm_l", "lowerarm_l", "hand_l"),
            "thigh":    ("thigh_l", "calf_l", "foot_l"),
        },
        "r": {
            "upperarm": ("upperarm_r", "lowerarm_r", "hand_r"),
            "thigh":    ("thigh_r", "calf_r", "foot_r"),
        }
    },
    "twist": {
        "l": {
            "upperarm": ("upperarm_l", "upperarm_twist_01_l", "upperarm_twist_02_l"),
            "lowerarm": ("hand_l", "lowerarm_twist_02_l", "lowerarm_twist_01_l"),
            "thigh":    ("thigh_l",    "thigh_twist_01_l",    "thigh_twist_02_l"),
            "calf":     ("foot_l",     "calf_twist_02_l",     "calf_twist_01_l"),
        },
        "r": {
            "upperarm": ("upperarm_r", "upperarm_twist_01_r", "upperarm_twist_02_r"),
            "lowerarm": ("hand_r", "lowerarm_twist_02_r", "lowerarm_twist_01_r"),
            "thigh":    ("thigh_r",    "thigh_twist_01_r",    "thigh_twist_02_r"),
            "calf":     ("foot_r",     "calf_twist_02_r",     "calf_twist_01_r"),
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


class RigOps:
    CTRL_SIZE_PRESET = {"large": 18.0, "medium": 10.0, "small": 2.0, }

    @staticmethod
    def _resolve_radius(size):
        if isinstance(size, (int, float)):
            return float(size)
        try:
            return RigOps.CTRL_SIZE_PRESET[size]
        except KeyError:
            raise RuntimeError(f"Unknown ctrl size tier: {size}")

    @staticmethod
    def create_ctrl_fk(**kwargs):
        args = dict(name="CTRL_FK", size="medium",
                    normal=(0, 1, 0), color_index=18)
        args.update(kwargs)

        radius = RigOps._resolve_radius(args["size"])

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

        extent = RigOps._resolve_radius(args["size"])

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

        extent = RigOps._resolve_radius(args["size"])
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
        args = dict(name="CTRL_IKFK", size="small", color_index=6)
        args.update(kwargs)

        extent = RigOps._resolve_radius(args["size"])
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

        radius = RigOps._resolve_radius(args["size"])

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
    def register_deform_skeleton(root):
        rig_root = get_or_create_rig_root()
        skeleton_grp = get_or_create_child(rig_root, "skeleton")
        deform_grp = get_or_create_child(skeleton_grp, "deform_joints")

        new_root = cmds.parent(root, deform_grp)[0]
        new_root = cmds.ls(new_root, long=True)[0]

        all_joints = [new_root] + (
            cmds.listRelatives(new_root, ad=True, type="joint", f=True) or [])

        for j in all_joints:
            short = j.split("|")[-1]
            RIG_CTX.joint_registry.setdefault("deform", {})[short] = j
        return new_root

    @staticmethod
    def build_ue5_FK_controls(root):
        LIMB_JOINTS = ["upperarm_l", "lowerarm_l", "hand_l",
                       "upperarm_r", "lowerarm_r", "hand_r",
                       "thigh_l", "calf_l", "foot_l",
                       "thigh_r", "calf_r", "foot_r"]
        SPINE_JOINTS = ["spine_01", "spine_02", "spine_03", "spine_04"]
        FINGER_CHAINS = {
            "l": {"thumb":  ("thumb_01_l",  "thumb_02_l",  "thumb_03_l"),
                  "index":  ("index_01_l",  "index_02_l",  "index_03_l"),
                  "middle": ("middle_01_l", "middle_02_l", "middle_03_l"),
                  "ring":   ("ring_01_l",   "ring_02_l",   "ring_03_l"),
                  "pinky":  ("pinky_01_l",  "pinky_02_l",  "pinky_03_l"), },
            "r": {"thumb":  ("thumb_01_r",  "thumb_02_r",  "thumb_03_r"),
                  "index":  ("index_01_r",  "index_02_r",  "index_03_r"),
                  "middle": ("middle_01_r", "middle_02_r", "middle_03_r"),
                  "ring":   ("ring_01_r",   "ring_02_r",   "ring_03_r"),
                  "pinky":  ("pinky_01_r",  "pinky_02_r",  "pinky_03_r"), }}

        rig_root = get_or_create_rig_root()
        controls_grp = get_or_create_child(rig_root, "controls")
        main_system = cmds.group(em=True, n="MainSystem", p=controls_grp)
        fk_system = cmds.group(em=True, n="FKSystem",   p=controls_grp)

        main_system = cmds.ls(main_system, long=True)[0]
        fk_system = cmds.ls(fk_system, long=True)[0]

        all_joints = [root]+cmds.listRelatives(
            root, ad=True, type="joint", fullPath=True) or []
        joint_map = {j.split("|")[-1]: j for j in all_joints}

        root_ctrl = RigOps.create_ctrl_fk(
            name="FK_root", size=34.0, normal=(0, 0, 1))
        cmds.matchTransform(root_ctrl, root)
        cmds.parent(root_ctrl, main_system)

        build_fk_chain_controls(joint_names=LIMB_JOINTS, joint_map=joint_map,
                                parent_grp=fk_system, size="medium")
        build_fk_chain_controls(joint_names=SPINE_JOINTS, joint_map=joint_map,
                                parent_grp=fk_system, size="large")

        for side, finger_dict in FINGER_CHAINS.items():
            grp = cmds.group(em=True, n=f"Fingers_{side}_GRP", p=fk_system)
            grp = cmds.ls(grp, long=True)[0]
            RIG_CTX.control_registry.setdefault(
                "finger_groups", {})[side] = grp

            for finger_name, chain in finger_dict.items():
                build_fk_chain_controls(joint_names=chain, joint_map=joint_map,
                                        parent_grp=grp, size="small")

        shapes = cmds.listRelatives(
            fk_system, ad=True, type="nurbsCurve", fullPath=True) or []

        for shape in shapes:
            ctrl = cmds.listRelatives(shape, parent=True, fullPath=True)[0]
            short = ctrl.split("|")[-1]
            short = short[:-3]

            RIG_CTX.control_registry.setdefault("fk", {})[short] = ctrl

    @staticmethod
    def build_ue5_IK_controls(root):
        JOINTS = ["hand_l", "hand_r", "foot_l", "foot_r",
                  "lowerarm_l", "lowerarm_r", "calf_l", "calf_r",
                  "spine_01", "spine_03", "spine_05"]

        all_joints = [root]+cmds.listRelatives(
            root, ad=True, type="joint", fullPath=True) or []
        joint_map = {j.split("|")[-1]: j for j in all_joints}

        rig_root = get_or_create_rig_root()
        controls_grp = get_or_create_child(rig_root, "controls")
        ik_system = cmds.group(em=True, n="IKSystem", p=controls_grp)
        ik_system = cmds.ls(ik_system, long=True)[0]

        spine_ctrls = {}
        for jnt_name in JOINTS:
            jnt = joint_map.get(jnt_name)

            if jnt_name.startswith(("hand", "foot", "spine")):
                size = "large" if jnt_name.startswith("spine") else "medium"
                ctrl = RigOps.create_ctrl_ik(name=f"{jnt_name}_ik", size=size)
                cmds.matchTransform(ctrl, jnt)
                parented_ctrl = cmds.parent(ctrl, ik_system)[0]
                ctrl_long = cmds.ls(parented_ctrl, long=True)[0]
                freeze_to_offset_parent_matrix(ctrl_long)
                if jnt_name.startswith("spine"):
                    spine_ctrls[jnt_name] = ctrl_long

            else:
                ctrl = RigOps.create_ctrl_pole_vector(name=f"{jnt_name}_pole")
                cmds.matchTransform(ctrl, jnt)

                offset = 40.0 if jnt_name.startswith("calf") else -40.0
                offset *= 1 if jnt_name.endswith("_r") else -1

                cmds.move(0, offset, 0, ctrl, r=True, os=True)
                cmds.setAttr(ctrl + ".rotate", 0, 0, 0)
                freeze_to_offset_parent_matrix(ctrl)

                cmds.addAttr(ctrl, ln="Follow", at="double",
                             min=0, max=10, dv=0)
                cmds.setAttr(ctrl + ".Follow", e=True, keyable=True)

                cmds.addAttr(ctrl, ln="Lock", at="double", min=0, max=10, dv=0)
                cmds.setAttr(ctrl + ".Lock", e=True, keyable=True)

                cmds.parent(ctrl, ik_system)

        shapes = cmds.listRelatives(
            ik_system, ad=True, type="nurbsCurve", fullPath=True) or []

        for shape in shapes:
            ctrl = cmds.listRelatives(shape, parent=True, fullPath=True)[0]
            short = ctrl.split("|")[-1]

            if short.endswith("_ik"):
                short = short[:-3]
                RIG_CTX.control_registry.setdefault("ik", {})[short] = ctrl
            elif short.endswith("_pole"):
                short = short[:-5]
                RIG_CTX.control_registry.setdefault("ik", {})[short] = ctrl

    @staticmethod
    def build_ikfk_switch_controls(root):
        ROOT_JOINTS = ["upperarm_l", "upperarm_r",
                       "thigh_l", "thigh_r", "spine_01"]

        all_joints = [root]+cmds.listRelatives(
            root, ad=True, type="joint", fullPath=True) or []
        joint_map = {j.split("|")[-1]: j for j in all_joints}

        rig_root = get_or_create_rig_root()
        controls_grp = get_or_create_child(rig_root, "controls")
        fkik_system = cmds.group(em=True, n="FKIKSystem", p=controls_grp)
        fkik_system = cmds.ls(fkik_system, long=True)[0]

        for jnt_name in ROOT_JOINTS:
            jnt = joint_map.get(jnt_name)
            ctrl = RigOps.create_ctrl_ikfk_switch(name=f"{jnt_name}_ikfk")
            cmds.matchTransform(ctrl, jnt)
            cmds.setAttr(ctrl + ".rotate", 0, 0, 0)

            offset_y = 0
            offset_x = 10.0 if jnt_name.endswith("_l") else -10.0
            if jnt_name.startswith("spine"):
                offset_x = 20.0
                offset_y = 10.0
            cmds.move(offset_x, offset_y, 0, ctrl, r=True, os=True)
            cmds.parent(ctrl, fkik_system)

            for attr in ("translateX", "translateY", "translateZ",
                         "rotateX", "rotateY", "rotateZ",
                         "scaleX", "scaleY", "scaleZ",
                         "visibility"):
                cmds.setAttr(f"{ctrl}.{attr}", lock=True,
                             keyable=False, channelBox=False)

            cmds.addAttr(ctrl, ln="IKFKBlend",
                         at="double", min=0, max=10, dv=0)
            cmds.setAttr(ctrl + ".IKFKBlend", e=True, keyable=True)

            cmds.addAttr(ctrl, ln="AutoVis", at="bool", dv=1)
            cmds.setAttr(ctrl + ".AutoVis", e=True,
                         keyable=False, channelBox=True)

            cmds.addAttr(ctrl, ln="FKVis", at="bool", dv=1)
            cmds.setAttr(ctrl + ".FKVis", e=True, keyable=True)

            cmds.addAttr(ctrl, ln="IKVis", at="bool", dv=1)
            cmds.setAttr(ctrl + ".IKVis", e=True, keyable=True)

        shapes = cmds.listRelatives(
            fkik_system, ad=True, type="nurbsCurve", fullPath=True) or []

        for shape in shapes:
            ctrl = cmds.listRelatives(shape, parent=True, fullPath=True)[0]
            short = ctrl.split("|")[-1]
            base = short.replace("_ikfk", "")

            RIG_CTX.control_registry.setdefault("ikfk", {})[base] = ctrl

    @staticmethod
    def build_ik_fk_skeletons(root):

        build_schema_skeleton(root, "limb", "ik")
        build_schema_skeleton(root, "limb", "fk")

        build_schema_skeleton(root, "spine", "ik")
        build_schema_skeleton(root, "spine", "fk")

    @staticmethod
    def build_ikfk_deform_drivers():
        IK_LIMB_CHAINS = {"upperarm_l": ("upperarm_l", "lowerarm_l", "hand_l"),
                          "upperarm_r": ("upperarm_r", "lowerarm_r", "hand_r"),
                          "thigh_l": ("thigh_l", "calf_l", "foot_l"),
                          "thigh_r": ("thigh_r", "calf_r", "foot_r")}

        ikfk_ctrls = RIG_CTX.control_registry.get("ikfk", {})
        fk_ctrls = RIG_CTX.control_registry.get("fk", {})
        ik_ctrls = RIG_CTX.control_registry.get("ik", {})

        fk_joints = RIG_CTX.joint_registry.get("fk", {})
        ik_joints = RIG_CTX.joint_registry.get("ik", {})
        deform_joints = RIG_CTX.joint_registry.get("deform", {})

        for limb, chain in IK_LIMB_CHAINS.items():
            ctrl = ikfk_ctrls.get(limb)
            ctrl_short = ctrl.split("|")[-1]

            md = cmds.createNode("multiplyDivide", n=f"{limb}_IKFKBlend_MD")
            cmds.setAttr(md + ".input2X", 0.1)
            cmds.connectAttr(f"{ctrl_short}.IKFKBlend",
                             md + ".input1X", force=True)

            rev = cmds.createNode("reverse", n=f"{limb}_IKFKBlend_REV")
            cmds.connectAttr(md + ".outputX", rev + ".inputX", force=True)

            for joint_name in chain:
                fk = fk_joints.get(joint_name)
                ik = ik_joints.get(joint_name)
                deform = deform_joints.get(joint_name)

                fk_ctrl = fk_ctrls.get(joint_name)
                ik_ctrl = ik_ctrls.get(joint_name)

                constraint = cmds.parentConstraint(fk, ik, deform, mo=False)[0]

                w0_attr = cmds.listAttr(constraint, string="*W0")[0]
                w1_attr = cmds.listAttr(constraint, string="*W1")[0]

                cmds.connectAttr(
                    md + ".outputX", f"{constraint}.{w0_attr}", force=True)
                cmds.connectAttr(
                    md + ".outputX", fk_ctrl + ".visibility", force=True)

                cmds.connectAttr(
                    rev + ".outputX", f"{constraint}.{w1_attr}", force=True)
                if joint_name.startswith(("upperarm", "thigh")):
                    continue
                cmds.connectAttr(
                    rev + ".outputX", ik_ctrl + ".visibility", force=True)

    @staticmethod
    def build_spine_deform_drivers():
        SPINE_CHAIN = {"deform": ("spine_01", "spine_02", "spine_03",
                                  "spine_04", "spine_05"),
                       "ik": ("spine_01", "spine_03", "spine_05"),
                       "fk": ("spine_01", "spine_02", "spine_03", "spine_04")}

        ikfk_ctrls = RIG_CTX.control_registry.get("ikfk", {})
        fk_ctrls = RIG_CTX.control_registry.get("fk", {})
        ik_ctrls = RIG_CTX.control_registry.get("ik", {})

        fk_joints = RIG_CTX.joint_registry.get("fk", {})
        ik_joints = RIG_CTX.joint_registry.get("ik", {})
        deform_joints = RIG_CTX.joint_registry.get("deform", {})

        ctrl = ikfk_ctrls.get("spine_01")
        ctrl_short = ctrl.split("|")[-1]

        md = cmds.createNode("multiplyDivide", n="spine_IKFKBlend_MD")
        cmds.setAttr(md + ".input2X", 0.1)
        cmds.connectAttr(f"{ctrl_short}.IKFKBlend",
                         md + ".input1X", force=True)

        rev = cmds.createNode("reverse", n=f"spine_IKFKBlend_REV")
        cmds.connectAttr(md + ".outputX", rev + ".inputX", force=True)

        for joint_name in SPINE_CHAIN["deform"]:
            fk = fk_joints.get(joint_name)
            ik = ik_joints.get(joint_name)
            deform = deform_joints.get(joint_name)

            constraint = cmds.parentConstraint(fk, ik, deform, mo=False)[0]

            w0_attr = cmds.listAttr(constraint, string="*W0")[0]
            w1_attr = cmds.listAttr(constraint, string="*W1")[0]
            cmds.connectAttr(
                md + ".outputX", f"{constraint}.{w0_attr}", force=True)
            cmds.connectAttr(
                rev + ".outputX", f"{constraint}.{w1_attr}", force=True)

        for j in SPINE_CHAIN["fk"]:
            fk_ctrl = fk_ctrls.get(j)
            cmds.connectAttr(
                md + ".outputX", fk_ctrl + ".visibility", force=True)

        for j in SPINE_CHAIN["ik"]:
            ik_ctrl = ik_ctrls.get(j)
            cmds.connectAttr(
                rev + ".outputX", ik_ctrl + ".visibility", force=True)

    @staticmethod
    def build_fk_joint_drivers():
        FINGER_JOINTS = ["thumb_01_l", "thumb_02_l", "thumb_03_l",
                         "thumb_01_r", "thumb_02_r", "thumb_03_r",
                         "index_01_l", "index_02_l", "index_03_l",
                         "index_01_r", "index_02_r", "index_03_r",
                         "middle_01_l", "middle_02_l", "middle_03_l",
                         "middle_01_r", "middle_02_r", "middle_03_r",
                         "ring_01_l", "ring_02_l", "ring_03_l",
                         "ring_01_r", "ring_02_r", "ring_03_r",
                         "pinky_01_l", "pinky_02_l", "pinky_03_l",
                         "pinky_01_r", "pinky_02_r", "pinky_03_r",]

        fk_ctrls = RIG_CTX.control_registry.get("fk", {})
        fk_joints = RIG_CTX.joint_registry.get("fk", {})
        deform_joints = RIG_CTX.joint_registry.get("deform", {})

        for ctrl_key, ctrl in fk_ctrls.items():
            joint_key = ctrl_key.replace("_fk", "")
            joint = fk_joints.get(joint_key)
            if joint_key in FINGER_JOINTS:
                continue

            freeze_to_offset_parent_matrix(ctrl)

            for attr in ("translate", "rotate"):
                cmds.connectAttr(f"{ctrl}.{attr}",
                                 f"{joint}.{attr}", force=True)

        for ctrl_key, ctrl in fk_ctrls.items():
            joint_key = ctrl_key.replace("_fk", "")
            joint = deform_joints.get(joint_key)
            if joint_key not in FINGER_JOINTS:
                continue

            freeze_to_offset_parent_matrix(ctrl)

            # cmds.parentConstraint(ctrl, joint, mo=False)

    @staticmethod
    def build_limb_ik_joint_drivers():
        IK_LIMB_CHAINS = {"upperarm_l": ("upperarm_l", "lowerarm_l", "hand_l"),
                          "upperarm_r": ("upperarm_r", "lowerarm_r", "hand_r"),
                          "thigh_l": ("thigh_l", "calf_l", "foot_l"),
                          "thigh_r": ("thigh_r", "calf_r", "foot_r")}
        IK_POLE_MAP = {"hand_l": "lowerarm_l",
                       "hand_r": "lowerarm_r",
                       "foot_l": "calf_l",
                       "foot_r": "calf_r"}
        joint_map = RIG_CTX.joint_registry.get("ik", {})
        ctrl_map = RIG_CTX.control_registry.get("ik", {})

        for _, (start_name, mid_name, end_name) in IK_LIMB_CHAINS.items():

            try:
                start_joint = joint_map[start_name]
                mid_joint = joint_map[mid_name]
                end_joint = joint_map[end_name]
            except KeyError:
                continue

            ik_handle, effector = cmds.ikHandle(
                sj=start_joint, ee=end_joint, sol="ikRPsolver", n=f"{end_name}_IKH")

            ik_ctrl = ctrl_map.get(f"{end_name}")
            cmds.orientConstraint(ik_ctrl, end_joint, mo=False)
            cmds.parent(ik_handle, ik_ctrl)

        for ik_key, pole_key in IK_POLE_MAP.items():
            ik_ctrl = ctrl_map.get(ik_key)
            pole_ctrl = ctrl_map.get(pole_key)

            ikh = cmds.listRelatives(
                ik_ctrl, ad=True, type="ikHandle", fullPath=True)[0]
            cmds.poleVectorConstraint(pole_ctrl, ikh)

    @staticmethod
    def build_spine_ik_joint_drivers():
        SPINE_JOINTS = {"spine_01", "spine_02",
                        "spine_03", "spine_04", "spine_05"}

        ik_joints = RIG_CTX.joint_registry.get("ik", {})
        ik_ctrls = RIG_CTX.control_registry.get("ik", {})

        joints = []
        for short, jnt in ik_joints.items():
            if short in SPINE_JOINTS:
                joints.append(jnt)

        joints.sort(key=lambda j: j.count("|"))
        points = [cmds.xform(j, q=True, ws=True, t=True)for j in joints]
        print(points)

        curve = cmds.curve(p=points, d=4, n="spine_ik_curve")

        start_joint = joints[0]
        end_joint = joints[-1]

        ik_handle, effector = cmds.ikHandle(sj=start_joint, ee=end_joint,
                                            sol="ikSplineSolver",
                                            c=curve, ccv=False, pcv=False)
        cmds.rename(ik_handle, "spine_ikHandle")

        parent_grp = cmds.listRelatives(ik_joints.get(
            "spine_01"), parent=True, fullPath=True)
        lower = cmds.duplicate(ik_joints.get("spine_01"),
                               parentOnly=True, name="lower_spine_ik")[0]
        mid = cmds.duplicate(ik_joints.get("spine_03"),
                             parentOnly=True, name="mid_spine_ik")[0]
        upper = cmds.duplicate(ik_joints.get("spine_05"),
                               parentOnly=True, name="upper_spine_ik")[0]
        cmds.parent([mid, upper], parent_grp)

        bind_joints = [lower, mid, upper]
        cmds.skinCluster(bind_joints, curve, tsb=True,
                         mi=1, nw=1,  name="spine_curve_skinCluster")

        ctrl_map = {"spine_01": lower, "spine_03": mid, "spine_05": upper}
        for spine_key, driver_jnt in ctrl_map.items():
            ctrl = ik_ctrls.get(spine_key)
            driver_jnt_full = cmds.ls(driver_jnt, long=True)[0]

            # freeze_to_offset_parent_matrix(driver_jnt_full)

            cmds.connectAttr(ctrl + ".rotate",
                             driver_jnt_full + ".rotate", force=True)
            cmds.connectAttr(ctrl + ".translate",
                             driver_jnt_full + ".translate", force=True)

        ctrl_01 = ik_ctrls.get("spine_01")
        ctrl_03 = ik_ctrls.get("spine_03")
        ctrl_05 = ik_ctrls.get("spine_05")
        ik_handle = cmds.ls("spine_ikHandle", long=True)[0]

        md = cmds.createNode("multiplyDivide", n="spine01_roll_twist_MD")
        cmds.setAttr(md + ".input2X", 1)
        cmds.setAttr(md + ".input2Y", -1)
        cmds.connectAttr(ctrl_01 + ".rotateX", md + ".input1X", force=True)
        cmds.connectAttr(ctrl_01 + ".rotateX", md + ".input1Y", force=True)

        pma = cmds.createNode("plusMinusAverage", n="spine_twist_sum_PMA")
        cmds.setAttr(pma + ".operation", 1)
        cmds.connectAttr(md + ".outputY", pma + ".input1D[0]", force=True)
        cmds.connectAttr(ctrl_05 + ".rotateX", pma + ".input1D[1]", force=True)
        cmds.connectAttr(ctrl_03 + ".rotateX", pma + ".input1D[2]", force=True)

        cmds.connectAttr(md + ".outputX", ik_handle + ".roll", force=True)
        cmds.connectAttr(pma + ".output1D", ik_handle + ".twist", force=True)

    @staticmethod
    def connect_upperarm_twist_deform():

        schema = UE5_SCHEMA.get("twist", {})

        deform_map = RIG_CTX.joint_registry.get("deform", {})

        for side, limb_dict in schema.items():
            for limb, chain in limb_dict.items():

                start_short, twist01_short, twist02_short = chain

                start_jnt = deform_map.get(start_short)
                twist01_jnt = deform_map.get(twist01_short)
                twist02_jnt = deform_map.get(twist02_short)

                freeze_to_offset_parent_matrix(start_jnt)
                freeze_to_offset_parent_matrix(twist01_jnt)
                freeze_to_offset_parent_matrix(twist02_jnt)

                src_attr = f"{start_jnt}.rotateX"
                dst01_attr = f"{twist01_jnt}.rotateX"
                dst02_attr = f"{twist02_jnt}.rotateX"

                md01_name = f"{twist01_short}_deformTwist_MD"
                md02_name = f"{twist02_short}_deformTwist_MD"

                md01 = cmds.createNode("multiplyDivide", n=md01_name)
                md02 = cmds.createNode("multiplyDivide", n=md02_name)

                cmds.setAttr(md01 + ".input2X", 0.33)
                cmds.setAttr(md02 + ".input2X", 0.66)

                cmds.connectAttr(src_attr, md01 + ".input1X", force=True)
                cmds.connectAttr(src_attr, md02 + ".input1X", force=True)

                cmds.connectAttr(md01 + ".outputX", dst01_attr, force=True)
                cmds.connectAttr(md02 + ".outputX", dst02_attr, force=True)

    @staticmethod
    def build_hand_controls(root):
        JOINTS = ["hand_l", "hand_r"]

        rig_root = get_or_create_rig_root()
        controls_grp = get_or_create_child(rig_root, "controls")
        dri_system = get_or_create_child(controls_grp, "DrivingSystem")
        finger_groups = RIG_CTX.control_registry.get("finger_groups", {})

        dri_system = cmds.ls(dri_system, long=True)[0]

        all_joints = [root]+cmds.listRelatives(
            root, ad=True, type="joint", fullPath=True) or []
        joint_map = {j.split("|")[-1]: j for j in all_joints}

        for jnt_name in JOINTS:
            side = jnt_name.split("_")[-1]
            hand_joint = joint_map.get(jnt_name)

            ctrl = RigOps.create_ctrl_half_circle(
                name=f"{jnt_name}_ctrl", size="medium", color_index=17)

            cmds.matchTransform(ctrl, hand_joint)

            if jnt_name.endswith("_l"):
                cmds.rotate(0, 90, 0, ctrl, r=True, os=True)
                cmds.move(0, 0, 12, ctrl, r=True, os=True)
            else:
                cmds.rotate(0, -90, 0, ctrl, r=True, os=True)
                cmds.move(0, 0, 12, ctrl, r=True, os=True)

            grp = finger_groups.get(side)

            cmds.parent(ctrl, grp)
            freeze_to_offset_parent_matrix(ctrl)

            shapes = cmds.listRelatives(
                grp, ad=True, type="nurbsCurve", fullPath=True) or []

            for shape in shapes:
                ctrl = cmds.listRelatives(shape, parent=True, fullPath=True)[0]
                short = ctrl.split("|")[-1]
                short = short[:-5]
                short = ctrl.split("|")[-1]

                if not short.endswith("_ctrl"):
                    continue

                RIG_CTX.control_registry.setdefault("hand", {})[short] = ctrl

    @staticmethod
    def build_hand_attributes():

        hand_schema = UE5_SCHEMA.get("hand", {})
        hand_ctrls = RIG_CTX.control_registry.get("hand", {})
        finger_ctrls = RIG_CTX.control_registry.get("fk", {})

        for hand_key, ctrl in hand_ctrls.items():

            cmds.addAttr(ctrl, ln="Spread",
                         at="double", min=-5, max=10, dv=0)
            cmds.setAttr(ctrl + ".Spread", e=True, keyable=True)

            side = hand_key.split("_")[1]
            side_chains = hand_schema.get(side, {})

            for finger_name, chain in side_chains.items():

                attr_name = f"{finger_name.capitalize()}_Curl"

                if not cmds.attributeQuery(attr_name, node=ctrl, exists=True):
                    cmds.addAttr(ctrl, ln=attr_name, at="double",
                                 min=-2, max=10, dv=0)
                    cmds.setAttr(f"{ctrl}.{attr_name}", e=True, keyable=True)

                md_name = f"{hand_key}_{finger_name}_Curl_MD"

                if not cmds.objExists(md_name):
                    md = cmds.createNode("multiplyDivide", n=md_name)
                    cmds.setAttr(f"{md}.input2X", 9)

                    cmds.connectAttr(f"{ctrl}.{attr_name}",
                                     f"{md}.input1X", force=True)
                else:
                    md = md_name

                for joint_name in chain:

                    if finger_name == "thumb" and joint_name.endswith("_01_" + side):
                        continue

                    fk_ctrl = finger_ctrls.get(joint_name)

                    cmds.connectAttr(
                        f"{md}.outputX", f"{fk_ctrl}.rotateZ", force=True)

            for attr in ("translateX", "translateY", "translateZ",
                         "rotateX", "rotateY", "rotateZ",
                         "scaleX", "scaleY", "scaleZ",
                         "visibility"):
                cmds.setAttr(f"{ctrl}.{attr}", lock=True,
                             keyable=False, channelBox=False)

    @staticmethod
    def connect_hand_to_finger_groups():

        finger_groups = RIG_CTX.control_registry.get("finger_groups", {})
        deform_joints = RIG_CTX.joint_registry.get("deform", {})

        for side, grp in finger_groups.items():

            grp = cmds.ls(grp, long=True)[0]

            hand_joint_name = f"hand_{side}"
            hand_joint = deform_joints.get(hand_joint_name)

            cmds.parentConstraint(hand_joint, grp, mo=True)[0]

    @staticmethod
    def auto_rig_lite_ue5(root):
        RIG_CTX.control_registry.clear()

        root = RigOps.register_deform_skeleton(root)

        RigOps.build_ue5_FK_controls(root)
        RigOps.build_ue5_IK_controls(root)
        RigOps.build_ikfk_switch_controls(root)

        RigOps.build_ik_fk_skeletons(root)
        RigOps.build_ikfk_deform_drivers()
        RigOps.build_spine_deform_drivers()

        RigOps.build_fk_joint_drivers()
        RigOps.build_limb_ik_joint_drivers()
        # RigOps.build_spine_ik_joint_drivers()

        RigOps.connect_upperarm_twist_deform()

        RigOps.build_hand_controls(root)
        RigOps.build_hand_attributes()
        RigOps.connect_hand_to_finger_groups()


def build_schema_skeleton(root_joint, category, suffix):
    # print(f"#######################{category}_{suffix}#######################")

    schema = UE5_SCHEMA.get(category, {})

    new_root = cmds.duplicate(root_joint, rr=True)[0]
    new_root = cmds.ls(new_root, long=True)[0]

    rig_root_grp = get_or_create_rig_root()
    skeleton_grp = get_or_create_child(rig_root_grp, "skeleton")
    joints_grp = get_or_create_child(skeleton_grp, f"{suffix}_joints")

    full_hierarchy = [new_root] + (
        cmds.listRelatives(new_root, ad=True, type="joint", f=True) or [])
    joint_by_short = {j.split("|")[-1]: j for j in full_hierarchy}

    for side_dict in schema.values():
        for root_name, chain in side_dict.items():
            base_joint = joint_by_short.get(chain[0])

            chain_grp = cmds.group(base_joint, name=f"{suffix}_{chain[0]}")
            chain_grp = cmds.parent(chain_grp, joints_grp)[0]

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
                cmds.rename(joint, f"{short}_{suffix}")

            for _, short in rename_queue:
                new_joint = cmds.ls(f"{short}_{suffix}", long=True)[0]
                freeze_to_offset_parent_matrix(new_joint)
                cmds.setAttr(new_joint + ".visibility", 0)
                RIG_CTX.joint_registry.setdefault(
                    suffix, {})[short] = new_joint

    cmds.delete(new_root)


def build_fk_chain_controls(joint_names, joint_map, parent_grp, size):
    joint_to_ctrl = {}

    for jnt_name in joint_names:
        jnt = joint_map.get(jnt_name)

        ctrl = RigOps.create_ctrl_fk(
            name=f"{jnt_name}_fk", size=size, normal=(1, 0, 0))

        cmds.matchTransform(ctrl, jnt)
        ctrl = cmds.parent(ctrl, parent_grp)
        ctrl = cmds.ls(ctrl, long=True)[0]

        joint_to_ctrl[jnt] = ctrl

    limb_sorted = sorted(joint_to_ctrl.keys(),
                         key=lambda j: j.count("|"), reverse=True)

    for jnt in limb_sorted:
        ctrl = joint_to_ctrl[jnt]

        parent = cmds.listRelatives(
            jnt, parent=True, type="joint", fullPath=True)
        while parent:
            parent_jnt = parent[0]
            parent_ctrl = joint_to_ctrl.get(parent_jnt)

            if parent_ctrl:
                cmds.parent(ctrl, parent_ctrl)
                break

            parent = cmds.listRelatives(
                parent_jnt, parent=True, type="joint", fullPath=True)


def get_or_create_rig_root():
    if cmds.objExists("RIG_ROOT"):
        return "RIG_ROOT"
    return cmds.group(em=True, n="RIG_ROOT")


def get_or_create_child(parent, name):
    path = f"{parent}|{name}"
    if cmds.objExists(path):
        return path
    return cmds.group(em=True, n=name, p=parent)


def freeze_to_offset_parent_matrix(node):
    m = cmds.xform(node, q=True, m=True, os=True)

    cmds.setAttr(node + ".offsetParentMatrix", *m, type="matrix")

    cmds.setAttr(node + ".translate", 0, 0, 0)
    cmds.setAttr(node + ".rotate", 0, 0, 0)
    cmds.setAttr(node + ".scale", 1, 1, 1)


def get_maya_window():
    ptr = omui.MQtUtil.mainWindow()
    return shiboken6.wrapInstance(int(ptr), QtWidgets.QWidget)


def show_square_ui():
    show_square_ui.instance = MySquareUI()
    show_square_ui.instance.show(dockable=True)
    return show_square_ui.instance


def debug_transform(node, label=""):
    node = cmds.ls(node, l=True)[0]
    t = cmds.xform(node, q=True, ws=True, t=True)
    r = cmds.xform(node, q=True, ws=True, ro=True)
    print(f"[DEBUG]{label} {node}")
    print(f"    T(ws): {t}")
    print(f"    R(ws): {r}")


RIG_CTX = RigBuildContext()

show_square_ui()
