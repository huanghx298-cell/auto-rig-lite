

import os
import importlib

import shiboken6
from PySide6 import QtWidgets, QtCore

import maya.cmds as cmds
import maya.OpenMayaUI as omui
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from rig import rig_runtime
from rig import ctrl_builder
from rig import rig_builders_body
from rig import rig_builders_hand_foot
from rig import rig_builders_deformation

from rig import rig_builders_space

from anim import animation_transfer

importlib.reload(rig_runtime)
importlib.reload(ctrl_builder)
importlib.reload(rig_builders_body)
importlib.reload(rig_builders_hand_foot)
importlib.reload(rig_builders_deformation)
importlib.reload(rig_builders_space)
importlib.reload(animation_transfer)


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

        self._add_button("Select Folder", self.on_select_folder)

        self.dropdown = QtWidgets.QComboBox()

        self.layout.addWidget(self.dropdown)

        self._add_button("Run", self.on_run_selected)

        self.on_select_folder()

    def on_debug(self):
        cmds.undoInfo(openChunk=True)
        try:
            solve_pole_vector_follow()
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

            RigBuilder.build_ue5_auto_rig(sel[0])
        except Exception as e:
            cmds.warning(str(e))
            raise
        finally:
            cmds.undoInfo(closeChunk=True)

    def _add_button(self, label, callback):
        btn = QtWidgets.QPushButton(label)
        btn.clicked.connect(callback)
        self.layout.addWidget(btn)
        return btn

    def on_select_folder(self):

        # folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder")

        folder = r"C:\Users\huang\Documents\maya\projects\auto_rig_Lite\assets\anim_retarget"
        if not folder:
            return

        self.current_folder = folder

        files = os.listdir(folder)

        files = [f for f in files if f.endswith((".ma", ".mb"))]

        self.dropdown.clear()
        self.dropdown.addItems(files)

    def on_run_selected(self):

        RIG_CTX.rebuild()

        if not hasattr(self, "current_folder"):
            cmds.warning("Please select a folder first")
            return

        filename = self.dropdown.currentText()
        full_path = os.path.join(self.current_folder, filename)

        cmds.undoInfo(openChunk=True)
        try:
            AnimBuilder.retarget_to_fk_ctrl(full_path)
        except Exception as e:
            cmds.warning(str(e))
            raise
        finally:
            cmds.undoInfo(closeChunk=True)

    def on_rebuild_registry(self):

        RIG_CTX.rebuild()
        print("\n===== CONTROL REGISTRY =====")

        for system, data in RIG_CTX.control_registry.items():
            print(f"\n[{system.upper()}]")
            for k, v in data.items():
                print(f"{k} -> {v}")


class RigBuilder:

    @staticmethod
    def build_limb_ikfk():

        SkeletonRig.build_limb_ikfk_skeletons()

        ControlBuilder.build_limb_fK_controls()
        ControlBuilder.build_limb_iK_controls()
        ControlBuilder.build_limb_ikfk_controls()

        LimbRig.build_limb_ikfk_deform_drivers()
        LimbRig.build_limb_fk_ctrl_joint_drivers()
        LimbRig.build_limb_ik_ctrl_joint_drivers()

        LimbRig.build_clavicle_fk_ctrl_joint_drivers()

    @staticmethod
    def build_spine_ikfk():

        SkeletonRig.build_spine_ikfk_skeletons()

        ControlBuilder.build_spine_fK_controls()
        ControlBuilder.build_spine_iK_controls()
        ControlBuilder.build_spine_ikfk_controls()
        ControlBuilder.build_hip_controls()

        SpineRig.build_spine_ik_curve()
        SpineRig.build_spine_curve_driver_joints()
        SpineRig.build_spine_ik_ctrl_follow_joints()

        SpineRig.build_spine_ikfk_deform_drivers()
        SpineRig.build_spine_fk_ctrl_joint_drivers()
        SpineRig.build_spine_ik_ctrl_curve_drivers()
        SpineRig.build_spine_ik_ctrl_curve_orient_drivers()
        SpineRig.build_spine_curve_ik_joint_drivers()

        SpineRig.build_spine_hip_ctrl_drivers()

    @staticmethod
    def build_hand():

        ControlBuilder.build_hand_controls()

        HandRig.build_hand_spread_attributes()
        HandRig.build_hand_curl_attributes()

        HandRig.build_finger_fk_deform_drivers()

    @staticmethod
    def build_foot():

        FootRig.build_roll_bank_skeleton()
        FootRig.build_roll_bank_iK_driver()
        FootRig.build_roll_driver()
        FootRig.build_bank_driver()

    @staticmethod
    def build_twist():

        TwistRig.build_twist_driver()
        TwistRig.build_twist_system()

    @staticmethod
    def build_head():

        ControlBuilder.build_head_controls()
        HeadRig.build_head_fk_deform_drivers()

    @staticmethod
    def build_space():

        SpaceSystem.build_clavicle_follow_spine_driver()
        SpaceSystem.build_thigh_follow_pelvis_drivers()
        SpaceSystem.build_head_follow_spine_driver()
        SpaceSystem.build_spine_start_end_mid_ctrl_driver()
        SpaceSystem.build_ik_fk_hand_ctrl_drivers()

    @staticmethod
    def build_ue5_auto_rig(root):

        RIG_CTX.clear()

        SkeletonRig.register_deform_skeleton(root)

        ControlBuilder.build_root_fK_controls()

        RigBuilder.build_limb_ikfk()
        RigBuilder.build_spine_ikfk()

        RigBuilder.build_hand()
        RigBuilder.build_foot()
        RigBuilder.build_head()

        RigBuilder.build_twist()

        RigBuilder.build_space()

        print("\n" + "=" * 60)
        print("AUTO RIG LITE UE5 BUILD SUCCESS")
        print("=" * 60 + "\n")


class AnimBuilder:

    @staticmethod
    def retarget_to_fk_ctrl(path):

        AnimTransfer.import_retarget_skeleton(path)
        AnimTransfer.build_retarget_bind_pose()
        AnimTransfer.build_retarget_fk_constraints()
        AnimTransfer.build_fk_ik_constraints()
        # AnimTransfer.build_fk_ik_pole_vector_driver()

    @staticmethod
    def bake_fk_to_ik_ctrl():

        AnimTransfer.build_fk_to_ik_constraints()


def get_maya_window():
    ptr = omui.MQtUtil.mainWindow()
    return shiboken6.wrapInstance(int(ptr), QtWidgets.QWidget)


def show_square_ui():
    show_square_ui.instance = MySquareUI()
    show_square_ui.instance.show(dockable=True)
    return show_square_ui.instance


def solve_pole_vector_follow():

    cubes = cmds.ls("pCube*", type="transform", long=True)
    cubes = sorted(cubes)

    thigh = cubes[0]
    pole = cubes[1]
    foot = cubes[2]
    target = cubes[3]

    print("=== Pole Vector Debug (Auto) ===")
    print(f"thigh  : {thigh}")
    print(f"pole   : {pole}")
    print(f"foot   : {foot}")
    print(f"target : {target}")

    thigh_pos = cmds.createNode("decomposeMatrix", n="thigh_DCM")
    pole_pos = cmds.createNode("decomposeMatrix", n="pole_DCM")
    foot_pos = cmds.createNode("decomposeMatrix", n="foot_DCM")

    cmds.connectAttr(f"{thigh}.worldMatrix[0]", f"{thigh_pos}.inputMatrix")
    cmds.connectAttr(f"{pole}.worldMatrix[0]", f"{pole_pos}.inputMatrix")
    cmds.connectAttr(f"{foot}.worldMatrix[0]", f"{foot_pos}.inputMatrix")

    thigh_to_foot = cmds.createNode("plusMinusAverage", n="thigh_to_foot")
    cmds.setAttr(f"{thigh_to_foot}.operation", 2)

    cmds.connectAttr(f"{foot_pos}.outputTranslate",
                     f"{thigh_to_foot}.input3D[0]")
    cmds.connectAttr(f"{thigh_pos}.outputTranslate",
                     f"{thigh_to_foot}.input3D[1]")

    thigh_to_pole = cmds.createNode("plusMinusAverage", n="thigh_to_pole")
    cmds.setAttr(f"{thigh_to_pole}.operation", 2)

    cmds.connectAttr(f"{pole_pos}.outputTranslate",
                     f"{thigh_to_pole}.input3D[0]")
    cmds.connectAttr(f"{thigh_pos}.outputTranslate",
                     f"{thigh_to_pole}.input3D[1]")

    dot = cmds.createNode("vectorProduct", n="dotProduct")
    cmds.setAttr(f"{dot}.operation", 1)

    cmds.connectAttr(f"{thigh_to_pole}.output3D", f"{dot}.input1")
    cmds.connectAttr(f"{thigh_to_foot}.output3D", f"{dot}.input2")

    foot_len_sq = cmds.createNode("vectorProduct", n="foot_len_sq")
    cmds.setAttr(f"{foot_len_sq}.operation", 1)

    cmds.connectAttr(f"{thigh_to_foot}.output3D", f"{foot_len_sq}.input1")
    cmds.connectAttr(f"{thigh_to_foot}.output3D", f"{foot_len_sq}.input2")

    scale = cmds.createNode("multiplyDivide", n="proj_scale")
    cmds.setAttr(f"{scale}.operation", 2)

    cmds.connectAttr(f"{dot}.outputX", f"{scale}.input1X")
    cmds.connectAttr(f"{foot_len_sq}.outputX", f"{scale}.input2X")

    proj = cmds.createNode("multiplyDivide", n="projection")
    cmds.setAttr(f"{proj}.operation", 1)

    cmds.connectAttr(f"{thigh_to_foot}.output3D", f"{proj}.input1")
    cmds.connectAttr(f"{scale}.outputX", f"{proj}.input2X")
    cmds.connectAttr(f"{scale}.outputX", f"{proj}.input2Y")
    cmds.connectAttr(f"{scale}.outputX", f"{proj}.input2Z")

    perp = cmds.createNode("plusMinusAverage", n="perpendicular")
    cmds.setAttr(f"{perp}.operation", 2)

    cmds.connectAttr(f"{thigh_to_pole}.output3D", f"{perp}.input3D[0]")
    cmds.connectAttr(f"{proj}.output", f"{perp}.input3D[1]")

    final_pos = cmds.createNode("plusMinusAverage", n="final_pos")
    cmds.setAttr(f"{final_pos}.operation", 1)

    cmds.connectAttr(f"{thigh_pos}.outputTranslate", f"{final_pos}.input3D[0]")
    cmds.connectAttr(f"{perp}.output3D", f"{final_pos}.input3D[1]")

    cmds.connectAttr(f"{final_pos}.output3D",
                     f"{target}.translate", force=True)


UE5_SCHEMA = rig_runtime.UE5_SCHEMA
RIG_CTX = rig_runtime.RIG_CTX

ControlBuilder = ctrl_builder.ControlBuilder

SkeletonRig = rig_builders_body.SkeletonRig
SpineRig = rig_builders_body.SpineRig
LimbRig = rig_builders_body.LimbRig
HandRig = rig_builders_hand_foot.HandRig
FootRig = rig_builders_hand_foot.FootRig
TwistRig = rig_builders_deformation.TwistRig
HeadRig = rig_builders_hand_foot.HeadRig

SpaceSystem = rig_builders_space.SpaceSystem

RigHelpers = rig_runtime.RigHelpers

AnimTransfer = animation_transfer.AnimTransfer

show_square_ui()
