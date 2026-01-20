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

        DEBUG_STEPS = False
        if DEBUG_STEPS:
            self._add_button("Create FK Control",
                             self.on_create_ctrl_fk)
            self._add_button("Create IK Control",
                             self.on_create_ctrl_ik)
            self._add_button("Create Pole Vector Control",
                             self.on_create_ctrl_pole_vector)
            self._add_button("Create IK/FK Switch Control",
                             self.on_create_ctrl_ikfk_switch)
            self._add_button("Register Deform Skeleton",
                             self.on_register_deform_skeleton)
            self._add_button("Build FK Rig",
                             self.on_build_ue5_FK_controls)
            self._add_button("Build IK Rig",
                             self.on_build_ue5_IK_controls)
            self._add_button("Build IK/FK Switch Rig",
                             self.on_build_ikfk_switch_controls)
            self._add_button("Build IK/FK Limb Skeletons",
                             self.on_build_ik_fk_limb_skeletons)
            self._add_button("Build Ikfk Deform Drivers",
                             self.on_build_ikfk_deform_drivers)
            self._add_button("Build FK Joint Drivers",
                             self.on_build_fk_joint_drivers)
            self._add_button("Build IK Handles",
                             self.on_build_ik_handles)
        self._add_button("AUTO RIG LITE (UE5)",
                         self.on_auto_rig_lite)

        self.layout.addStretch()

    def on_create_ctrl_fk(self):
        cmds.undoInfo(openChunk=True)
        try:
            ctrl = RigOps.create_ctrl_fk()
            cmds.select(ctrl, r=True)
        except Exception as e:
            cmds.warning(str(e))
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_create_ctrl_ik(self):
        cmds.undoInfo(openChunk=True)
        try:
            ctrl = RigOps.create_ctrl_ik()
            cmds.select(ctrl, r=True)
        except Exception as e:
            cmds.warning(str(e))
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_create_ctrl_pole_vector(self):
        cmds.undoInfo(openChunk=True)
        try:
            ctrl = RigOps.create_ctrl_pole_vector()
            cmds.select(ctrl, r=True)
        except Exception as e:
            cmds.warning(str(e))
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_create_ctrl_ikfk_switch(self):
        cmds.undoInfo(openChunk=True)
        try:
            ctrl = RigOps.create_ctrl_ikfk_switch()
            cmds.select(ctrl, r=True)
        except Exception as e:
            cmds.warning(str(e))
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_register_deform_skeleton(self):
        cmds.undoInfo(openChunk=True)
        try:
            sel = cmds.ls(sl=True, type="joint", long=True)
            if not sel:
                raise RuntimeError("Select skeleton root joint")

            RigOps.register_deform_skeleton(sel[0])
        except Exception as e:
            cmds.warning(str(e))
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_build_ue5_FK_controls(self):
        cmds.undoInfo(openChunk=True)
        try:
            sel = cmds.ls(sl=True, type="joint", long=True)
            if not sel:
                raise RuntimeError("Please select skeleton root joint")

            RigOps.build_ue5_FK_controls(sel[0])
        except Exception as e:
            cmds.warning(str(e))
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_build_ue5_IK_controls(self):
        cmds.undoInfo(openChunk=True)
        try:
            sel = cmds.ls(sl=True, type="joint", long=True)
            if not sel:
                raise RuntimeError("Please select skeleton root joint")

            RigOps.build_ue5_IK_controls(sel[0])
        except Exception as e:
            cmds.warning(str(e))
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_build_ikfk_switch_controls(self):
        cmds.undoInfo(openChunk=True)
        try:
            sel = cmds.ls(sl=True, type="joint", long=True)
            if not sel:
                raise RuntimeError("Please select skeleton root joint")

            RigOps.build_ikfk_switch_controls(sel[0])
        except Exception as e:
            cmds.warning(str(e))
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_build_ik_fk_limb_skeletons(self):
        cmds.undoInfo(openChunk=True)
        try:
            sel = cmds.ls(sl=True, type="joint", long=True)
            if not sel:
                raise RuntimeError("Please select skeleton root joint")

            RigOps.build_ik_fk_limb_skeletons(sel[0])
        except Exception as e:
            cmds.warning(str(e))
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_build_ikfk_deform_drivers(self):
        cmds.undoInfo(openChunk=True)
        try:
            RigOps.build_ikfk_deform_drivers()
        except Exception as e:
            cmds.warning(str(e))
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_build_fk_joint_drivers(self):
        cmds.undoInfo(openChunk=True)
        try:
            RigOps.build_fk_joint_drivers()
        except Exception as e:
            cmds.warning(str(e))
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_build_ik_handles(self):
        cmds.undoInfo(openChunk=True)
        try:
            RigOps.build_ik_handles()
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
    CTRL_SIZE_PRESET = {"large": 18.0, "medium": 10.0, "small": 4.0, }

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
        h = extent * 0.5

        p000 = (-h, -h, -h)
        p001 = (-h, -h,  h)
        p010 = (-h,  h, -h)
        p011 = (-h,  h,  h)
        p100 = (h, -h, -h)
        p101 = (h, -h,  h)
        p110 = (h,  h, -h)
        p111 = (h,  h,  h)

        points = [p000, p100, p101, p001, p000, p010, p110,
                  p111, p011, p010, p110, p100, p101, p111,
                  p011, p001]

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
        LIMB_CHAINS = ["upperarm_l", "lowerarm_l", "hand_l",
                       "upperarm_r", "lowerarm_r", "hand_r",
                       "thigh_l", "calf_l", "foot_l",
                       "thigh_r", "calf_r", "foot_r"]
        SPINE_JOINTS = ["pelvis", "spine_01",
                        "spine_02", "spine_03", "spine_04"]

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

        joint_to_ctrl = {}

        for jnt_name in SPINE_JOINTS + LIMB_CHAINS:
            jnt = joint_map.get(jnt_name)
            if not jnt:
                cmds.warning(f"Joint not found under root: {jnt_name}")
                continue

            size = "large" if jnt_name in SPINE_JOINTS else "medium"
            ctrl = RigOps.create_ctrl_fk(
                name=f"{jnt_name}_fk", size=size, normal=(1, 0, 0))

            cmds.matchTransform(ctrl, jnt)
            ctrl = cmds.parent(ctrl, fk_system)
            ctrl = cmds.ls(ctrl, long=True)[0]

            joint_to_ctrl[jnt] = ctrl

        sorted_joints = sorted(joint_to_ctrl.keys(),
                               key=lambda j: j.count("|"), reverse=True)

        for jnt in sorted_joints:
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
                  "lowerarm_l", "lowerarm_r", "calf_l", "calf_r"]

        all_joints = [root]+cmds.listRelatives(
            root, ad=True, type="joint", fullPath=True) or []
        joint_map = {j.split("|")[-1]: j for j in all_joints}

        rig_root = get_or_create_rig_root()
        controls_grp = get_or_create_child(rig_root, "controls")
        ik_system = cmds.group(em=True, n="IKSystem", p=controls_grp)
        ik_system = cmds.ls(ik_system, long=True)[0]

        for jnt_name in JOINTS:
            jnt = joint_map.get(jnt_name)

            if jnt_name.startswith(("hand", "foot")):
                ctrl = RigOps.create_ctrl_ik(name=f"{jnt_name}_ik")
                cmds.matchTransform(ctrl, jnt)
                cmds.parent(ctrl, ik_system)

            else:
                ctrl = RigOps.create_ctrl_pole_vector(name=f"{jnt_name}_pole")
                cmds.matchTransform(ctrl, jnt)

                cmds.setAttr(ctrl + ".rotate", 0, 0, 0)

                offset = 40.0 if jnt.startswith("calf") else -40.0
                cmds.move(0, 0, offset, ctrl, r=True, os=True)

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
        ROOT_JOINTS = ["upperarm_l", "upperarm_r", "thigh_l", "thigh_r"]

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

            offset = 10.0 if jnt.endswith("_l") else -10.0
            cmds.move(offset, 0, 0, ctrl, r=True, os=True)
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
    def build_ik_fk_limb_skeletons(root):

        build_limb_skeleton(root_joint=root, suffix="ik",)
        build_limb_skeleton(root_joint=root, suffix="fk")

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
    def build_fk_joint_drivers():
        LIMB_JOINTS = {"upperarm_l", "lowerarm_l", "hand_l",
                       "upperarm_r", "lowerarm_r", "hand_r",
                       "thigh_l", "calf_l", "foot_l",
                       "thigh_r", "calf_r", "foot_r"}

        fk_ctrls = RIG_CTX.control_registry.get("fk", {})
        fk_joints = RIG_CTX.joint_registry.get("fk", {})

        for short, ctrl in fk_ctrls.items():
            base = short.replace("_fk", "")

            if base not in LIMB_JOINTS:
                continue

            joint = fk_joints.get(base)

            freeze_to_offset_parent_matrix(ctrl)
            freeze_to_offset_parent_matrix(joint)

            for attr in ("translate", "rotate"):
                cmds.connectAttr(f"{ctrl}.{attr}",
                                 f"{joint}.{attr}", force=True)

    @staticmethod
    def build_ik_handles():
        IK_LIMB_CHAINS = {"upperarm_l": ("upperarm_l", "lowerarm_l", "hand_l"),
                          "upperarm_r": ("upperarm_r", "lowerarm_r", "hand_r"),
                          "thigh_l": ("thigh_l", "calf_l", "foot_l"),
                          "thigh_r": ("thigh_r", "calf_r", "foot_r")}
        joint_map = RIG_CTX.joint_registry.get("ik", {})
        ctrl_map = RIG_CTX.control_registry.get("ik", {})

        for _, (start_name, mid_name, end_name) in IK_LIMB_CHAINS.items():

            try:
                start_joint = joint_map[start_name]
                mid_joint = joint_map[mid_name]
                end_joint = joint_map[end_name]
            except KeyError:
                continue

            for jnt in (start_joint, mid_joint, end_joint):
                freeze_to_offset_parent_matrix(jnt)

            ik_handle, effector = cmds.ikHandle(
                sj=start_joint, ee=end_joint, sol="ikRPsolver", n=f"{end_name}_IKH")

            ik_ctrl = ctrl_map.get(f"{end_name}")
            cmds.parent(ik_handle, ik_ctrl)

    @staticmethod
    def auto_rig_lite_ue5(root):
        RIG_CTX.control_registry.clear()

        root = RigOps.register_deform_skeleton(root)
        RigOps.build_ue5_FK_controls(root)
        RigOps.build_ue5_IK_controls(root)
        RigOps.build_ikfk_switch_controls(root)
        RigOps.build_ik_fk_limb_skeletons(root)
        RigOps.build_ikfk_deform_drivers()
        RigOps.build_fk_joint_drivers()
        RigOps.build_ik_handles()


def build_limb_skeleton(root_joint, suffix):
    target_joints = ["upperarm_r", "upperarm_l",
                     "thigh_r", "thigh_l"]

    LIMB_JOINTS = {"upperarm_l", "lowerarm_l", "hand_l",
                   "upperarm_r", "lowerarm_r", "hand_r",
                   "thigh_l", "calf_l", "foot_l",
                   "thigh_r", "calf_r", "foot_r"}

    new_root = cmds.duplicate(root_joint, rr=True)[0]
    new_root = cmds.ls(new_root, long=True)[0]

    rig_root = get_or_create_rig_root()
    skeleton_grp = get_or_create_child(rig_root, "skeleton")
    limb_joints_grp = cmds.group(em=True, n=suffix, p=skeleton_grp)

    full_hierarchy = [new_root] + (
        cmds.listRelatives(new_root, ad=True, type="joint", f=True) or [])
    joint_by_short = {j.split("|")[-1]: j for j in full_hierarchy}

    for base_name in target_joints:
        limb_root = joint_by_short.get(base_name)

        parent_transform = cmds.parent(limb_root, limb_joints_grp)[0]
        parent_transform = cmds.rename(
            parent_transform.split("|", 1)[0], f"{base_name}_{suffix}")

        limb_root = cmds.listRelatives(
            parent_transform, c=True, type="joint", f=True)[0]
        limb_joints = [limb_root] + (
            cmds.listRelatives(limb_root, ad=True, type="joint", f=True) or [])

        limb_joints.sort(key=lambda x: x.count("|"), reverse=True)

        rename_queue = []

        for joint in limb_joints:
            short = joint.split("|")[-1]
            if short in LIMB_JOINTS:
                rename_queue.append((joint, short))
            else:
                cmds.delete(joint)

        rename_queue.sort(key=lambda x: x[0].count("|"), reverse=True)

        for joint, short in rename_queue:
            new_joint = cmds.rename(joint, f"{short}_{suffix}")

        for _, short in rename_queue:
            new_joint = cmds.ls(f"{short}_{suffix}", long=True)[0]
            cmds.setAttr(new_joint + ".visibility", 0)
            RIG_CTX.joint_registry.setdefault(suffix, {})[short] = new_joint

    cmds.delete(new_root)


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


RIG_CTX = RigBuildContext()

show_square_ui()
