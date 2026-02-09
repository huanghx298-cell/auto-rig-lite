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
            self._add_button("Connect Deform Twist (X)",
                             self.on_connect_deform_twist_chain)
            self._add_button("Build IK/FK Limb Skeletons",
                             self.on_build_ik_fk_limb_skeletons)
            self._add_button("Build Ikfk Deform Drivers",
                             self.on_build_ikfk_deform_drivers)
            self._add_button("Build Ikfk Spine Deform Drivers",
                             self.on_build_spine_deform_drivers)
            self._add_button("Build FK Joint Drivers",
                             self.on_build_fk_joint_drivers)
            self._add_button("Build IK Handles",
                             self.on_build_limb_ik_joint_drivers)
            self._add_button("Build Spine IK Handles",
                             self.on_build_spine_ik_joint_drivers)
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

    def on_connect_deform_twist_chain(self):
        cmds.undoInfo(openChunk=True)
        try:
            RigOps.connect_deform_twist_chain()
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

    def on_build_spine_deform_drivers(self):
        cmds.undoInfo(openChunk=True)
        try:
            RigOps.build_spine_deform_drivers()
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

    def on_build_limb_ik_joint_drivers(self):
        cmds.undoInfo(openChunk=True)
        try:
            RigOps.build_limb_ik_joint_drivers()
        except Exception as e:
            cmds.warning(str(e))
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_build_spine_ik_joint_drivers(self):
        cmds.undoInfo(openChunk=True)
        try:
            curve = RigOps.build_spine_ik_joint_drivers()
            cmds.select(curve, r=True)
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
        SPINE_JOINTS = ["spine_01", "spine_02", "spine_03", "spine_04"]

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

        build_fk_chain_controls(joint_names=LIMB_CHAINS, joint_map=joint_map,
                                parent_grp=fk_system, size="medium")
        build_fk_chain_controls(joint_names=SPINE_JOINTS, joint_map=joint_map,
                                parent_grp=fk_system, size="large")

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

        for jnt_name in JOINTS:
            jnt = joint_map.get(jnt_name)

            if jnt_name.startswith(("hand", "foot", "spine")):
                ctrl = RigOps.create_ctrl_ik(name=f"{jnt_name}_ik")
                cmds.matchTransform(ctrl, jnt)
                parented_ctrl = cmds.parent(ctrl, ik_system)[0]
                ctrl_long = cmds.ls(parented_ctrl, long=True)[0]
                freeze_to_offset_parent_matrix(ctrl_long)

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
    def build_ik_fk_limb_skeletons(root):

        build_limb_skeleton(root_joint=root, suffix="ik")
        build_limb_skeleton(root_joint=root, suffix="fk")

    @staticmethod
    def connect_deform_twist_chain():
        DEFORM_TWIST_RULES = {
            "lowerarm_l": ("upperarm_twist_01_l", "upperarm_twist_02_l"),
            "lowerarm_r": ("upperarm_twist_01_r", "upperarm_twist_02_r"),
            "hand_l": ("lowerarm_twist_01_l", "lowerarm_twist_02_l"),
            "hand_r": ("lowerarm_twist_01_r", "lowerarm_twist_02_r"),
            "calf_l":    ("thigh_twist_01_l",    "thigh_twist_02_l"),
            "calf_r":    ("thigh_twist_01_r",    "thigh_twist_02_r"),
            "foot_l":     ("calf_twist_01_l",     "calf_twist_02_l"),
            "foot_r":     ("calf_twist_01_r",     "calf_twist_02_r"), }

        deform_joints = RIG_CTX.joint_registry.get("deform", {})

        for driver_name, (twist1_name, twist2_name) in DEFORM_TWIST_RULES.items():
            driver = deform_joints.get(driver_name)
            twist1 = deform_joints.get(twist1_name)
            twist2 = deform_joints.get(twist2_name)

            driver_base_rx = cmds.getAttr(driver + ".rotateX")
            twist1_base_rx = cmds.getAttr(twist1 + ".rotateX")
            twist2_base_rx = cmds.getAttr(twist2 + ".rotateX")

            driver_delta = cmds.createNode(
                "plusMinusAverage", n=f"{driver_name}_delta_PMA")
            cmds.setAttr(driver_delta + ".operation", 2)
            cmds.connectAttr(driver + ".rotateX",
                             driver_delta + ".input1D[0]", force=True)
            cmds.setAttr(driver_delta + ".input1D[1]", driver_base_rx)

            md1 = cmds.createNode(
                "multiplyDivide", n=f"{driver_name}_twist01_MD")
            cmds.setAttr(md1 + ".input2X", 0.33)
            cmds.connectAttr(driver_delta + ".output1D",
                             md1 + ".input1X", force=True)
            twist_sum1 = cmds.createNode(
                "plusMinusAverage", n=f"{driver_name}_twist01_PMA")
            cmds.setAttr(twist_sum1 + ".operation", 1)  # sum
            cmds.setAttr(twist_sum1 + ".input1D[0]", twist1_base_rx)
            cmds.connectAttr(md1 + ".outputX", twist_sum1 +
                             ".input1D[1]", force=True)
            cmds.connectAttr(twist_sum1 + ".output1D",
                             twist1 + ".rotateX", force=True)

            md2 = cmds.createNode(
                "multiplyDivide", n=f"{driver_name}_twist02_MD")
            cmds.setAttr(md2 + ".input2X", 0.66)
            cmds.connectAttr(driver_delta + ".output1D",
                             md2 + ".input1X", force=True)
            twist_sum2 = cmds.createNode(
                "plusMinusAverage", n=f"{driver_name}_twist02_PMA")
            cmds.setAttr(twist_sum2 + ".operation", 1)  # sum
            cmds.setAttr(twist_sum2 + ".input1D[0]", twist2_base_rx)
            cmds.connectAttr(md2 + ".outputX", twist_sum2 +
                             ".input1D[1]", force=True)
            cmds.connectAttr(twist_sum2 + ".output1D",
                             twist2 + ".rotateX", force=True)

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
        LIMB_JOINTS = {"upperarm_l", "lowerarm_l", "hand_l",
                       "upperarm_r", "lowerarm_r", "hand_r",
                       "thigh_l", "calf_l", "foot_l",
                       "thigh_r", "calf_r", "foot_r",
                       "spine_01", "spine_02", "spine_03", "spine_04"}

        fk_ctrls = RIG_CTX.control_registry.get("fk", {})
        fk_joints = RIG_CTX.joint_registry.get("fk", {})

        for short, ctrl in fk_ctrls.items():
            base = short.replace("_fk", "")
            joint = fk_joints.get(base)

            freeze_to_offset_parent_matrix(ctrl)
            freeze_to_offset_parent_matrix(joint)

            for attr in ("translate", "rotate"):
                cmds.connectAttr(f"{ctrl}.{attr}",
                                 f"{joint}.{attr}", force=True)

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

            for jnt in (start_joint, mid_joint, end_joint):
                freeze_to_offset_parent_matrix(jnt)

            ik_handle, effector = cmds.ikHandle(
                sj=start_joint, ee=end_joint, sol="ikRPsolver", n=f"{end_name}_IKH")

            ik_ctrl = ctrl_map.get(f"{end_name}")
            cmds.connectAttr(f"{ik_ctrl}.rotate",
                             f"{end_joint}.rotate", force=True)
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

            freeze_to_offset_parent_matrix(driver_jnt_full)

            cmds.connectAttr(ctrl + ".rotate",
                             driver_jnt_full + ".rotate", force=True)
            cmds.connectAttr(ctrl + ".translate",
                             driver_jnt_full + ".translate", force=True)

    @staticmethod
    def auto_rig_lite_ue5(root):
        RIG_CTX.control_registry.clear()

        root = RigOps.register_deform_skeleton(root)
        RigOps.build_ue5_FK_controls(root)
        RigOps.build_ue5_IK_controls(root)
        RigOps.build_ikfk_switch_controls(root)
        RigOps.build_ik_fk_limb_skeletons(root)
        RigOps.connect_deform_twist_chain()
        RigOps.build_ikfk_deform_drivers()
        RigOps.build_spine_deform_drivers()
        RigOps.build_fk_joint_drivers()
        RigOps.build_limb_ik_joint_drivers()
        RigOps.build_spine_ik_joint_drivers()


def build_limb_skeleton(root_joint, suffix):
    target_joints = ["upperarm_r", "upperarm_l",
                     "thigh_r", "thigh_l", "spine_01"]

    LIMB_JOINTS = {"upperarm_l", "lowerarm_l", "hand_l",
                   "upperarm_r", "lowerarm_r", "hand_r",
                   "thigh_l", "calf_l", "foot_l",
                   "thigh_r", "calf_r", "foot_r",
                   "spine_01", "spine_02", "spine_03", "spine_04", "spine_05"}

    new_root = cmds.duplicate(root_joint, rr=True)[0]
    new_root = cmds.ls(new_root, long=True)[0]

    rig_root_grp = get_or_create_rig_root()
    skeleton_grp = get_or_create_child(rig_root_grp, "skeleton")
    limb_joints_grp = cmds.group(em=True, n=suffix, p=skeleton_grp)

    full_hierarchy = [new_root] + (
        cmds.listRelatives(new_root, ad=True, type="joint", f=True) or [])
    joint_by_short = {j.split("|")[-1]: j for j in full_hierarchy}

    for base_name in target_joints:
        limb_root = joint_by_short.get(base_name)

        limb_grp = cmds.group(limb_root, name=f"{suffix}_{base_name}")
        limb_grp = cmds.parent(limb_grp, limb_joints_grp)[0]

        limb_root = cmds.listRelatives(
            limb_grp, c=True, type="joint", f=True)[0]
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
            # cmds.setAttr(new_joint + ".visibility", 0)
            RIG_CTX.joint_registry.setdefault(suffix, {})[short] = new_joint

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
