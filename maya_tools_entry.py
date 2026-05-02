

import os
import importlib

import shiboken6
from PySide6 import QtWidgets, QtCore

import maya.cmds as cmds
import maya.OpenMayaUI as omui
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from rig import rig_builders_runtime
from rig import rig_builders_ctrl
from rig import rig_builders_body
from rig import rig_builders_hand_foot
from rig import rig_builders_deformation
from rig import rig_builders_space

from anim import animation_runtime
from anim import animation_transfer
from anim import animation_locomotion

importlib.reload(rig_builders_runtime)
importlib.reload(rig_builders_ctrl)
importlib.reload(rig_builders_body)
importlib.reload(rig_builders_hand_foot)
importlib.reload(rig_builders_deformation)
importlib.reload(rig_builders_space)

importlib.reload(animation_runtime)
importlib.reload(animation_transfer)
importlib.reload(animation_locomotion)


class MySquareUI(MayaQWidgetDockableMixin, QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent or get_maya_window())

        self.rig_ctx = RIG_CTX
        self.anim_ctx = ANIM_CTX

        self.animbuilder = AnimBuilder()

        self.setWindowTitle("Auto Rig & Animation Toolkit")
        self.resize(300, 300)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(QtWidgets.QLabel(
            "Rigging & Retargeting & Root Motion"))
        self.build_basic_tools(self.layout)

        self.dropdown = QtWidgets.QComboBox()
        self.layout.addWidget(self.dropdown)

        self.card_list = QtWidgets.QListWidget()
        self.card_list.setDragDropMode(
            QtWidgets.QAbstractItemView.InternalMove)
        self.card_list.setDropIndicatorShown(True)
        layout_row = QtWidgets.QHBoxLayout()
        self.build_place_section(layout_row)
        self.layout.addLayout(layout_row)
        self.layout.addWidget(QtWidgets.QLabel("Reorder Cards"))
        self.layout.addWidget(self.card_list)
        self.build_root_motion_section(self.layout)

        # self.rig_ctx.rebuild()

        self.reload_scene()
        self.populate_dropdown_from_registry()
        # self.on_run_selected()

    def build_basic_tools(self, layout):
        self._add_button("Run Full Pipeline", self.debug, layout)
        self._add_button("AUTO RIG (UE5)", self.build_auto_rig, layout)
        self._add_button("Reopen current scene", self.reload_scene, layout)
        layout.addStretch()

    def debug(self):
        sel = cmds.ls("root", type="joint", long=True)[0]
        self.run_with_undo(RigBuilder.build_auto_rig, sel)
        folder = r"C:\Users\huang\Documents\maya\projects\auto_rig_Lite\assets\anim_retarget"

        files = os.listdir(folder)
        files = [f for f in files if f.endswith((".ma", ".mb"))]
        file_name = files[0]

        self.full_path = os.path.join(folder, file_name)
        file_name = os.path.splitext(os.path.basename(self.full_path))[0]

        cmds.refresh(suspend=True)

        self.run_with_undo(
            self.animbuilder.build_retarget_fk_ik_ctrl, self.full_path, file_name)

        file_name = "Walking_Anim"
        self.run_with_undo(self.animbuilder.preview_root_motion, file_name)

        ikfk_ctrls = RIG_CTX.control_registry.get("ikfk", {})

        start = int(cmds.playbackOptions(query=True, minTime=True))
        end = int(cmds.playbackOptions(query=True, maxTime=True))

        one_third = start + (end - start) / 3
        two_third = int(start + (end - start) * 2 / 3)

        for name, ctrl in ikfk_ctrls.items():

            cmds.setKeyframe(ctrl, attribute="IKFKBlend", time=start, value=0)

            cmds.setKeyframe(ctrl, attribute="IKFKBlend",
                             time=one_third, value=5)
            cmds.setKeyframe(ctrl, attribute="IKFKBlend",
                             time=two_third, value=5)

            cmds.setKeyframe(ctrl, attribute="IKFKBlend", time=end, value=10)

        cmds.currentTime(0)
        cmds.hide(f"skeleton")
        cmds.select(clear=True)

        cmds.refresh(suspend=False)

    def build_auto_rig(self):
        sel = cmds.ls("root", type="joint", long=True)[0]
        self.run_with_undo(RigBuilder.build_auto_rig, sel)

    def reload_scene(self):

        scene = cmds.file(query=True, sceneName=True)
        cmds.file(scene, open=True, force=True)

        self.rig_ctx.rebuild()
        self.anim_ctx.rebuild()

        self.card_list.clear()
        groups = self.anim_ctx.path_registry.get("root_motion_groups")
        for group in groups:
            item = QtWidgets.QListWidgetItem(group)
            item.setSizeHint(QtCore.QSize(100, 40))
            self.card_list.addItem(item)

        self.current_active_file = None

    def on_run_selected(self):

        # Warning:
        # Reopening the current scene here is safe when running manually.
        # But if this function is triggered automatically on scene load
        # (e.g. via userSetup or scriptJob), it may cause an infinite reload loop.

        folder = r"C:\Users\huang\Documents\maya\projects\auto_rig_Lite\assets\anim_retarget"

        files = os.listdir(folder)
        files = [f for f in files if f.endswith((".ma", ".mb"))]
        file_name = files[0]

        self.full_path = os.path.join(folder, file_name)
        file_name = os.path.splitext(os.path.basename(self.full_path))[0]

        self.run_with_undo(
            self.animbuilder.build_retarget_fk_ik_ctrl, self.full_path, file_name)

    def populate_dropdown_from_registry(self):
        registry = self.anim_ctx.retarget_joint_registry
        names = list(registry.keys())
        self.dropdown.addItems(names)

    def build_place_section(self, layout):
        self.current_active_file = None
        self._add_button("Place Animation", self.place_animation, layout)
        self.btn_done = self._add_button("Done", self.done, layout)
        self.btn_done.setEnabled(False)

    def place_animation(self):
        file_name = self.dropdown.currentText()
        if self.current_active_file:
            self.run_with_undo(
                self.animbuilder.build_root_motion, self.current_active_file)
        self.run_with_undo(self.animbuilder.setup_root_motion_edit, file_name)
        current_group = self.anim_ctx.path_registry["current_root_motion_group"]
        item = QtWidgets.QListWidgetItem(current_group)
        item.setSizeHint(QtCore.QSize(100, 40))
        self.card_list.addItem(item)
        self.current_active_file = file_name

        self.btn_done.setEnabled(True)
        self.btn_preview.setEnabled(False)

    def done(self):
        file_name = self.dropdown.currentText()
        self.run_with_undo(self.animbuilder.build_root_motion, file_name)
        self.btn_done.setEnabled(False)
        self.btn_preview.setEnabled(True)
        self.current_active_file = None

    def build_root_motion_section(self, layout):
        self.current_preview_file = None
        self.btn_preview = self._add_button(
            "Preview", self.preview_root_motion, layout)
        self._add_button("Finalize", self.finalize_root_motion, layout)
        self.btn_preview.setEnabled(True)

    def preview_root_motion(self):

        file_name = self.dropdown.currentText()

        order = []
        for i in range(self.card_list.count()):
            item = self.card_list.item(i)
            order.append(item.text())
        self.anim_ctx.path_registry["root_motion_groups"] = order

        for index, group in enumerate(order):
            meta = cmds.ls(f"{group}_animMeta", type="network")[0]
            cmds.setAttr(f"{meta}.order", index)

        self.run_with_undo(self.animbuilder.preview_root_motion, file_name)

    def finalize_root_motion(self):
        self.run_with_undo(self.animbuilder.finalize_root_motion)

    def _add_button(self, label, callback, layout):
        btn = QtWidgets.QPushButton(label)
        btn.clicked.connect(callback)
        layout.addWidget(btn)
        return btn

    def run_with_undo(self, func, *args):
        cmds.undoInfo(openChunk=True)
        try:
            return func(*args)
        except Exception as e:
            cmds.warning(str(e))
            raise
        finally:
            cmds.undoInfo(closeChunk=True)


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

        SpaceSystem.build_root_ik_fk_ctrl_drivers()

    @staticmethod
    def build_auto_rig(root):

        RIG_CTX.clear()

        SkeletonRig.register_deform_skeleton(root)

        ControlBuilder.build_root_fK_controls()

        RigBuilder.build_limb_ikfk()
        RigBuilder.build_spine_ikfk()

        RigBuilder.build_hand()
        RigBuilder.build_foot()
        RigBuilder.build_head()

        # RigBuilder.build_twist()

        RigBuilder.build_space()

        print("\n" + "=" * 60)
        print("AUTO RIG LITE UE5 BUILD SUCCESS")
        print("=" * 60 + "\n")


class AnimBuilder:

    def __init__(self):

        self.animtransfer = AnimTransfer()
        self.animpath = AnimPath()
        self.locomotion = AnimLocomotion()

    def build_retarget_fk_ik_ctrl(self, file_path, file_name):

        self.animtransfer.import_retarget_skeleton(file_path)
        self.animtransfer.build_retarget_bind_pose()
        self.animtransfer.build_retarget_fk_constraints()
        self.animtransfer.build_limb_retarget_ik_constraints()
        self.animtransfer.build_spine_retarget_ik_constraints()
        self.locomotion.locomotion_setup_foot_lock_reference()
        self.animpath.setup_root_motion_curve_locator()
        self.animtransfer.remove_retarget_bind_pose()
        self.locomotion.locomotion_base_distance(file_name)

    def setup_root_motion_edit(self, file_name):

        self.animpath.setup_root_motion_edit(file_name)

    def build_root_motion(self, file_name):

        self.locomotion.create_pose_reference()
        self.animpath.get_root_motion_positions(file_name)
        self.animpath.cache_root_motion_positions(file_name)
        self.animpath.build_root_motion_curve()

    def preview_root_motion(self, file_name):

        self.animpath.build_root_motion_curve()
        # self.animpath.apply_root_motion_pathsssss()
        self.animpath.setup_root_motion_path()
        self.animpath.apply_root_motion_path(file_name)

    def finalize_root_motion(self):

        self.locomotion.locomotion_get_foot_lock_ranges()
        self.locomotion.foot_ik_lock()


def get_maya_window():
    ptr = omui.MQtUtil.mainWindow()
    return shiboken6.wrapInstance(int(ptr), QtWidgets.QWidget)


def show_square_ui():
    show_square_ui.instance = MySquareUI()
    show_square_ui.instance.show(dockable=True)
    return show_square_ui.instance


RIG_CTX = rig_builders_runtime.RIG_CTX
ANIM_CTX = animation_runtime.ANIM_CTX

ControlBuilder = rig_builders_ctrl.ControlBuilder

SkeletonRig = rig_builders_body.SkeletonRig
SpineRig = rig_builders_body.SpineRig
LimbRig = rig_builders_body.LimbRig
HandRig = rig_builders_hand_foot.HandRig
FootRig = rig_builders_hand_foot.FootRig
TwistRig = rig_builders_deformation.TwistRig
HeadRig = rig_builders_hand_foot.HeadRig

SpaceSystem = rig_builders_space.SpaceSystem


AnimTransfer = animation_transfer.AnimationTransfer
AnimPath = animation_transfer.AnimationPath
AnimLocomotion = animation_locomotion.AnimationLocomotion


show_square_ui()
