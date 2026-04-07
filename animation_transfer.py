

import maya.cmds as cmds

from rig import rig_runtime


class AnimTransfer:

    @staticmethod
    def import_retarget_skeleton(path):

        retarget_group = cmds.group(empty=True, name="retarget_group")
        cmds.setAttr(f"{retarget_group}.visibility", 0)
        new_nodes = cmds.file(path, i=True,
                              importFrameRate=True, importTimeRange="override",
                              returnNewNodes=True)

        transform = cmds.ls(new_nodes, type="transform", long=True)[0]
        cmds.parent(transform, retarget_group)

        cmds.playbackOptions(minTime=-1)
        cmds.currentTime(-1)

        retarget_joints = cmds.listRelatives(
            retarget_group, allDescendents=True, type="joint", fullPath=True)
        for joint in retarget_joints:
            joint_name = joint.split("|")[-1]
            RIG_CTX.joint_registry.setdefault(
                "retarget", {})[joint_name] = joint

    @staticmethod
    def build_retarget_bind_pose():

        deform_joints = RIG_CTX.joint_registry.get("deform", {})
        retarget_joints = RIG_CTX.joint_registry.get("retarget", {})

        constraints = []
        for joint_name, deform_joint in deform_joints.items():
            retarget_joint = retarget_joints.get(joint_name)
            constraint = cmds.parentConstraint(deform_joint, retarget_joint)[0]
            constraints.append(constraint)

        joints = list(retarget_joints.values())

        cmds.bakeResults(joints, time=(-1, -1),
                         simulation=True, preserveOutsideKeys=True)

        joint = retarget_joints.get("thigh_r")
        cmds.filterCurve(joint, filter="euler")

        cmds.delete(constraints)

    @staticmethod
    def build_retarget_fk_constraints():

        constraint_group = RigHelpers.get_or_create_group_chain(
            "retarget_group", "retarget_fk_constraints")

        retarget_joints = RIG_CTX.joint_registry.get("retarget", {})

        fk_ctrls = RIG_CTX.control_registry.get("fk", {})
        ikfk_ctrls = RIG_CTX.control_registry.get("ikfk", {})

        for ikfk_ctrl in ikfk_ctrls.values():
            cmds.setAttr(f"{ikfk_ctrl}.IKFKBlend", 10)

        for joint_name, fk_ctrl in fk_ctrls.items():
            retarget_joint = retarget_joints.get(joint_name)
            constraint = cmds.parentConstraint(retarget_joint, fk_ctrl)[0]
            cmds.parent(constraint, constraint_group)

    @staticmethod
    def build_fk_ik_constraints():

        schema = UE5_SCHEMA.get("limb", {})

        fk_ctrls = RIG_CTX.control_registry.get("fk", {})
        ik_ctrls = RIG_CTX.control_registry.get("ik", {})
        ikfk_ctrls = RIG_CTX.control_registry.get("ikfk", {})

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                if limb_name == "thigh":
                    ikfk_key = f"{limb_name}_{side}"
                    ikfk_ctrl = ikfk_ctrls.get(ikfk_key)
                    cmds.setAttr(f"{ikfk_ctrl}.IKFKBlend", 0)

                if limb_name == "upperarm":
                    end_joint = chain[-1]
                else:
                    end_joint = chain[-2]

                ik_ctrl = ik_ctrls.get(end_joint)
                fk_ctrl = fk_ctrls.get(end_joint)

                group = cmds.group(
                    empty=True, name=f"{end_joint}_ikBuffer_GRP", parent=fk_ctrl)
                cmds.matchTransform(group, ik_ctrl)
                RigHelpers.bake_transform_to_opm(group)

                cmds.parentConstraint(group, ik_ctrl)

        cmds.playbackOptions(minTime=0)

    @staticmethod
    def build_fk_ik_pole_vector_driver():

        schema = UE5_SCHEMA.get("limb", {})

        fk_ctrls = RIG_CTX.control_registry.get("fk", {})
        ik_ctrls = RIG_CTX.control_registry.get("ik", {})

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                if limb_name == "upperarm":
                    continue

                prefix = f"{limb_name}_{side}"

                start_ctrl_name = chain[0]
                mid_ctrl_name = chain[1]
                end_ctrl_name = chain[2]

                start_ctrl = fk_ctrls.get(start_ctrl_name)
                mid_ctrl = fk_ctrls.get(mid_ctrl_name)
                end_ctrl = fk_ctrls.get(end_ctrl_name)

                driver_group = cmds.group(
                    empty=True, name=f"{prefix}_pvDriver_GRP")

                start_pos = cmds.createNode(
                    "decomposeMatrix", name=f"{prefix}_start_DCM")
                mid_pos = cmds.createNode(
                    "decomposeMatrix", name=f"{prefix}_mid_DCM")
                end_pos = cmds.createNode(
                    "decomposeMatrix", name=f"{prefix}_end_DCM")

                cmds.connectAttr(f"{start_ctrl}.worldMatrix[0]",
                                 f"{start_pos}.inputMatrix")
                cmds.connectAttr(f"{mid_ctrl}.worldMatrix[0]",
                                 f"{mid_pos}.inputMatrix")
                cmds.connectAttr(f"{end_ctrl}.worldMatrix[0]",
                                 f"{end_pos}.inputMatrix")

                # world-space positions

                start_to_end = cmds.createNode(
                    "plusMinusAverage", name=f"{prefix}_start_to_end_VEC")
                cmds.setAttr(f"{start_to_end}.operation", 2)
                cmds.connectAttr(f"{end_pos}.outputTranslate",
                                 f"{start_to_end}.input3D[0]")
                cmds.connectAttr(f"{start_pos}.outputTranslate",
                                 f"{start_to_end}.input3D[1]")

                start_to_mid = cmds.createNode(
                    "plusMinusAverage", name=f"{prefix}_start_to_mid_VEC")
                cmds.setAttr(f"{start_to_mid}.operation", 2)
                cmds.connectAttr(f"{mid_pos}.outputTranslate",
                                 f"{start_to_mid}.input3D[0]")
                cmds.connectAttr(f"{start_pos}.outputTranslate",
                                 f"{start_to_mid}.input3D[1]")

                # build vectors

                dot = cmds.createNode(
                    "vectorProduct", name=f"{prefix}_dotProduct")
                cmds.setAttr(f"{dot}.operation", 1)
                cmds.connectAttr(f"{start_to_mid}.output3D",
                                 f"{dot}.input1")
                cmds.connectAttr(f"{start_to_end}.output3D",
                                 f"{dot}.input2")

                end_len_sq = cmds.createNode(
                    "vectorProduct", name=f"{prefix}_endLenSq")
                cmds.setAttr(f"{end_len_sq}.operation", 1)
                cmds.connectAttr(f"{start_to_end}.output3D",
                                 f"{end_len_sq}.input1")
                cmds.connectAttr(f"{start_to_end}.output3D",
                                 f"{end_len_sq}.input2")

                scale = cmds.createNode(
                    "multiplyDivide", name=f"{prefix}_projScale")
                cmds.setAttr(f"{scale}.operation", 2)
                cmds.connectAttr(f"{dot}.outputX",
                                 f"{scale}.input1X")
                cmds.connectAttr(f"{end_len_sq}.outputX",
                                 f"{scale}.input2X")

                proj = cmds.createNode(
                    "multiplyDivide", name=f"{prefix}_projection")
                cmds.setAttr(f"{proj}.operation", 1)
                cmds.connectAttr(f"{start_to_end}.output3D",
                                 f"{proj}.input1")
                cmds.connectAttr(f"{scale}.outputX",
                                 f"{proj}.input2X")
                cmds.connectAttr(f"{scale}.outputX",
                                 f"{proj}.input2Y")
                cmds.connectAttr(f"{scale}.outputX",
                                 f"{proj}.input2Z")

                # compute projection vector

                perp = cmds.createNode(
                    "plusMinusAverage", name=f"{prefix}_perpendicular")
                cmds.setAttr(f"{perp}.operation", 2)
                cmds.connectAttr(f"{start_to_mid}.output3D",
                                 f"{perp}.input3D[0]")
                cmds.connectAttr(f"{proj}.output",
                                 f"{perp}.input3D[1]")

                # compute perpendicular vector

                final_pos = cmds.createNode(
                    "plusMinusAverage", name=f"{prefix}_finalPos")
                cmds.setAttr(f"{final_pos}.operation", 1)
                cmds.connectAttr(f"{start_pos}.outputTranslate",
                                 f"{final_pos}.input3D[0]")
                cmds.connectAttr(f"{perp}.output3D",
                                 f"{final_pos}.input3D[1]")

                cmds.connectAttr(f"{final_pos}.output3D",
                                 f"{driver_group}.translate")

    @staticmethod
    def bake_retarget_to_fk_ctrls():

        constraint_group = RigHelpers.get_or_create_group_chain(
            "retarget_group", "retarget_fk_constraints")

        fk_ctrls = RIG_CTX.control_registry.get("fk", {})

        bake_targets = list(fk_ctrls.values())
        end = cmds.playbackOptions(query=True, maxTime=True)
        cmds.bakeResults(bake_targets, time=(0, end),
                         simulation=True, sampleBy=1,
                         disableImplicitControl=True, preserveOutsideKeys=True,
                         sparseAnimCurveBake=False)

        cmds.delete(constraint_group)


RigHelpers = rig_runtime.RigHelpers
RIG_CTX = rig_runtime.RIG_CTX
UE5_SCHEMA = rig_runtime.UE5_SCHEMA
