

import maya.cmds as cmds

from rig import rig_runtime


class SpaceSystem:

    @staticmethod
    def build_clavicle_follow_spine_driver():

        fk_ctrls = RIG_CTX.control_registry.get("fk", {})

        spine_fk_joint = RIG_CTX.joint_registry.get("fk", {}).get("spine_05")
        spine_ik_joint = RIG_CTX.joint_registry.get("ik", {}).get("spine_05")

        for side in ("l", "r"):

            clavicle_ctrl_grp = cmds.listRelatives(
                fk_ctrls[f"clavicle_{side}"], parent=True, fullPath=True)[0]

            fk_follow_group = RigHelpers.create_group_parented_matched(
                name=f"fk_clavicle_{side}_follow_GRP",
                parent=spine_fk_joint,
                match=clavicle_ctrl_grp)
            ik_follow_group = RigHelpers.create_group_parented_matched(
                name=f"ik_clavicle_{side}_follow_GRP",
                parent=spine_ik_joint,
                match=clavicle_ctrl_grp)

            md = cmds.ls("spine_c_IKFKBlend_MD", long=True)[0]
            rev = cmds.ls("spine_c_IKFKBlend_REV", long=True)[0]

            constraint = cmds.parentConstraint(
                fk_follow_group, ik_follow_group, clavicle_ctrl_grp)[0]

            w0_attr = cmds.listAttr(constraint, string="*W0")[0]
            w1_attr = cmds.listAttr(constraint, string="*W1")[0]

            cmds.connectAttr(f"{md}.outputX",
                             f"{constraint}.{w0_attr}")
            cmds.connectAttr(f"{rev}.outputX",
                             f"{constraint}.{w1_attr}")

    @staticmethod
    def build_thigh_follow_pelvis_drivers():

        fk_ctrls = RIG_CTX.control_registry.get("fk", {})

        fk_joints = RIG_CTX.joint_registry.get("fk", {})
        ik_joints = RIG_CTX.joint_registry.get("ik", {})

        pelvis_fk_joint = cmds.ls("spine_01_hipFollow_GRP", long=True)[0]
        pelvis_ik_joint = ik_joints.get("pelvis")

        md = cmds.ls("spine_c_IKFKBlend_MD", long=True)[0]
        rev = cmds.ls("spine_c_IKFKBlend_REV", long=True)[0]

        for side in ("l", "r"):

            ik_joint = ik_joints[f"thigh_{side}"]
            ik_joint_group = cmds.listRelatives(
                ik_joint, parent=True, fullPath=True)[0]

            fk_ctrl = fk_ctrls.get(f"thigh_{side}")
            fk_ctrl_group = cmds.listRelatives(
                fk_ctrl, parent=True, fullPath=True)[0]

            targets = [("joint", ik_joint_group),
                       ("ctrl", fk_ctrl_group)]

            for tag, target_group in targets:

                fk_follow_group = RigHelpers.create_group_parented_matched(
                    name=f"fk_thigh_{side}_{tag}_follow_GRP",
                    parent=pelvis_fk_joint,
                    match=target_group)
                ik_follow_group = RigHelpers.create_group_parented_matched(
                    name=f"ik_thigh_{side}_{tag}_follow_GRP",
                    parent=pelvis_ik_joint,
                    match=target_group)

                constraint = cmds.parentConstraint(
                    fk_follow_group, ik_follow_group, target_group)[0]

                w0_attr = cmds.listAttr(constraint, string="*W0")[0]
                w1_attr = cmds.listAttr(constraint, string="*W1")[0]

                cmds.connectAttr(f"{md}.outputX",
                                 f"{constraint}.{w0_attr}")
                cmds.connectAttr(f"{rev}.outputX",
                                 f"{constraint}.{w1_attr}")

    @staticmethod
    def build_head_follow_spine_driver():

        spine_fk_joint = RIG_CTX.joint_registry.get("fk", {}).get("spine_05")
        spine_ik_joint = RIG_CTX.joint_registry.get("ik", {}).get("spine_05")

        head_ctrl_grp = RIG_CTX.group_registry.get("fk_ctrl", {}).get("head_c")

        fk_follow_group = RigHelpers.create_group_parented_matched(
            name=f"fk_head_c_follow_GRP",
            parent=spine_fk_joint,
            match=head_ctrl_grp)
        ik_follow_group = RigHelpers.create_group_parented_matched(
            name=f"ik_head_c_follow_GRP",
            parent=spine_ik_joint,
            match=head_ctrl_grp)

        md = cmds.ls("spine_c_IKFKBlend_MD", long=True)[0]
        rev = cmds.ls("spine_c_IKFKBlend_REV", long=True)[0]

        constraint = cmds.parentConstraint(
            fk_follow_group, ik_follow_group, head_ctrl_grp)[0]

        w0_attr = cmds.listAttr(constraint, string="*W0")[0]
        w1_attr = cmds.listAttr(constraint, string="*W1")[0]

        cmds.connectAttr(f"{md}.outputX",
                         f"{constraint}.{w0_attr}")
        cmds.connectAttr(f"{rev}.outputX",
                         f"{constraint}.{w1_attr}")

    @staticmethod
    def build_spine_start_end_mid_ctrl_driver():

        schema = UE5_SCHEMA.get("spine", {})

        ik_ctrls = RIG_CTX.control_registry.get("ik", {})

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                start_ctrl = ik_ctrls.get(chain[1])
                mid_ctrl = ik_ctrls.get(chain[2])
                end_ctrl = ik_ctrls.get(chain[3])

                ctrl_group = cmds.listRelatives(
                    mid_ctrl, parent=True, fullPath=True)[0]

                constraint = cmds.parentConstraint(
                    start_ctrl, end_ctrl, ctrl_group, maintainOffset=True)[0]

                w0 = cmds.listAttr(constraint, string="*W0")[0]
                w1 = cmds.listAttr(constraint, string="*W1")[0]

                cmds.setAttr(f"{constraint}.{w0}", 0.5)
                cmds.setAttr(f"{constraint}.{w1}", 0.5)

    @staticmethod
    def build_ik_fk_hand_ctrl_drivers():

        schema = UE5_SCHEMA.get("hand", {})

        constraint_system = RigHelpers.get_or_create_group_chain(
            "Group", "driving_system", "constraints")

        ikfk_ctrls = RIG_CTX.control_registry.get("ikfk", {})

        fk_joints = RIG_CTX.joint_registry.get("fk", {})
        ik_joints = RIG_CTX.joint_registry.get("ik", {})
        deform_joints = RIG_CTX.joint_registry.get("deform", {})

        fk_groups = RIG_CTX.group_registry.get("fk_ctrl", {})

        for side, side_dict in schema.items():

            chain_group = cmds.group(
                empty=True, name=f"constraint_hand_{side}_GRP",
                parent=constraint_system)

            fk_joint = fk_joints.get(f"hand_{side}")
            ik_joint = ik_joints.get(f"hand_{side}")
            deform_joint = deform_joints.get(f"hand_{side}")
            group = fk_groups.get(f"hand_{side}")

            ikfk_ctrl_short = ikfk_ctrls.get(f"upperarm_{side}").split("|")[-1]
            md = cmds.ls(f"{ikfk_ctrl_short}_IKFKBlend_MD", long=True)[0]
            rev = cmds.ls(f"{ikfk_ctrl_short}_IKFKBlend_REV", long=True)[0]

            fk_follow_group = RigHelpers.create_group_parented_matched(
                name=f"fk_hand_{side}_follow_GRP",
                parent=fk_joint,
                match=deform_joint)
            ik_follow_group = RigHelpers.create_group_parented_matched(
                name=f"ik_hand_{side}_follow_GRP",
                parent=ik_joint,
                match=deform_joint)

            constraint = cmds.parentConstraint(
                fk_follow_group, ik_follow_group, group)[0]

            w0_attr = cmds.listAttr(constraint, string="*W0")[0]
            w1_attr = cmds.listAttr(constraint, string="*W1")[0]

            cmds.connectAttr(f"{md}.outputX",
                             f"{constraint}.{w0_attr}")
            cmds.connectAttr(f"{rev}.outputX",
                             f"{constraint}.{w1_attr}")

            cmds.parent(constraint, chain_group)


RigHelpers = rig_runtime.RigHelpers
RIG_CTX = rig_runtime.RIG_CTX
UE5_SCHEMA = rig_runtime.UE5_SCHEMA
