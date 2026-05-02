

import maya.cmds as cmds

from rig import rig_builders_runtime


class HandRig:

    @staticmethod
    def build_hand_spread_attributes():

        schema = UE5_SCHEMA.get("hand", {})

        hand_ctrls = RIG_CTX.control_registry.get("hand", {})
        finger_ctrls = RIG_CTX.control_registry.get("fk", {})

        weights = {"index":  1.0,
                   "middle": 0.0,
                   "ring": -1.0,
                   "pinky": -2.0, }

        for side, side_dict in schema.items():

            hand_ctrl = hand_ctrls.get(f"hand_{side}")
            cmds.addAttr(hand_ctrl, longName="Spread", attributeType="double",
                         minValue=-5, maxValue=10, defaultValue=0, keyable=True)
            for attr in ("t", "r", "s"):
                for axis in "xyz":
                    cmds.setAttr(f"{hand_ctrl}.{attr}{axis}", lock=True,
                                 keyable=False, channelBox=False)
            cmds.setAttr(f"{hand_ctrl}.visibility", lock=True,
                         keyable=False, channelBox=False)

            for limb_name, chain in side_dict.items():
                if limb_name == "thumb":
                    continue

                w = weights.get(limb_name)
                fk_ctrl = finger_ctrls.get(chain[0])

                md = cmds.createNode(
                    "multiplyDivide", name=f"hand_{side}_{limb_name}_Spread_MD")
                cmds.setAttr(f"{md}.input2X", w)
                cmds.connectAttr(f"{hand_ctrl}.Spread",
                                 f"{md}.input1X")
                cmds.connectAttr(f"{md}.outputX",
                                 f"{fk_ctrl}.rotateY")

    @staticmethod
    def build_hand_curl_attributes():

        schema = UE5_SCHEMA.get("hand", {})

        hand_ctrls = RIG_CTX.control_registry.get("hand", {})
        finger_ctrls = RIG_CTX.control_registry.get("fk", {})

        for side, side_dict in schema.items():

            hand_ctrl = hand_ctrls.get(f"hand_{side}")

            for limb_name, chain in side_dict.items():

                attr_name = f"{limb_name.capitalize()}_Curl"

                if limb_name == "thumb":

                    cmds.addAttr(hand_ctrl, longName=attr_name, attributeType="double",
                                 minValue=-2, maxValue=10, defaultValue=0,
                                 keyable=True)

                    md01 = cmds.createNode(
                        "multiplyDivide", name=f"hand_{attr_name}_MD")
                    cmds.setAttr(f"{md01}.input2X", 4)
                    cmds.connectAttr(f"{hand_ctrl}.{attr_name}",
                                     f"{md01}.input1X")
                    fk_ctrl_01 = finger_ctrls.get(chain[0])
                    cmds.connectAttr(f"{md01}.outputX",
                                     f"{fk_ctrl_01}.rotateZ")

                    md02 = cmds.createNode(
                        "multiplyDivide", name=f"hand_thumb23_Curl_MD")
                    cmds.setAttr(f"{md02}.input2X", 8)
                    cmds.connectAttr(f"{hand_ctrl}.{attr_name}",
                                     f"{md02}.input1X")
                    for joint_name in chain[1:]:
                        fk_ctrl = finger_ctrls.get(joint_name)
                        cmds.connectAttr(f"{md02}.outputX",
                                         f"{fk_ctrl}.rotateZ")
                else:

                    cmds.addAttr(hand_ctrl, longName=attr_name, attributeType="double",
                                 minValue=-2, maxValue=10, defaultValue=0,
                                 keyable=True)

                    md = cmds.createNode(
                        "multiplyDivide", name=f"hand_{attr_name}_MD")
                    cmds.setAttr(f"{md}.input2X", 9)
                    cmds.connectAttr(f"{hand_ctrl}.{attr_name}",
                                     f"{md}.input1X")
                    for joint_name in chain:
                        fk_ctrl = finger_ctrls.get(joint_name)
                        cmds.connectAttr(f"{md}.outputX",
                                         f"{fk_ctrl}.rotateZ")

    @staticmethod
    def build_finger_fk_deform_drivers():

        schema = UE5_SCHEMA.get("hand", {})

        constraint_system = RigHelpers.get_or_create_group_chain(
            "Group", "driving_system", "constraints")

        fk_ctrls = RIG_CTX.control_registry.get("fk", {})

        deform_joints = RIG_CTX.joint_registry.get("deform", {})

        for side, side_dict in schema.items():

            chain_group = cmds.group(
                empty=True, name=f"constraint_hand_{side}_GRP",
                parent=constraint_system)

            for limb_name, chain in side_dict.items():
                for joint_name in chain:

                    fk_ctrl = fk_ctrls.get(joint_name)
                    deform_joint = deform_joints.get(joint_name)

                    constraint = cmds.parentConstraint(
                        fk_ctrl, deform_joint, maintainOffset=False)

                    cmds.parent(constraint, chain_group)


class FootRig:

    @staticmethod
    def build_roll_bank_skeleton():

        schema = UE5_SCHEMA.get("foot", {})

        foot_system = RigHelpers.get_or_create_group_chain(
            "Group", "driving_system", "foot_roll_system")

        ik_ctrls = RIG_CTX.control_registry.get("ik", {})

        ik_joints = RIG_CTX.joint_registry.get("ik", {})

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                foot_short, ball_short = chain
                ik_joint_ball = ik_joints.get(ball_short)
                ik_joint_foot = ik_joints.get(foot_short)

                ik_ctrl = ik_ctrls.get(foot_short)

                side_sign = 1 if side == "l" else -1

                group = cmds.group(
                    empty=True, name=f"{limb_name}_{side}_GRP", parent=foot_system)
                cmds.matchTransform(group, ik_ctrl)
                RigHelpers.bake_transform_to_opm(group)
                group = cmds.ls(group, long=True)[0]
                RIG_CTX.group_registry.setdefault(
                    "foot_pivot", {})[f"{limb_name}_{side}"] = group

                bank_inner_group = cmds.group(
                    empty=True, name=f"{foot_short}_bankInner__GRP",
                    parent=group)
                bank_outer_group = cmds.group(
                    empty=True, name=f"{foot_short}_bankOuter_GRP",
                    parent=bank_inner_group)
                roll_heel_joint = cmds.joint(
                    name=f"{foot_short}_heelPivot_JNT")
                roll_toe_joint = cmds.joint(
                    name=f"{foot_short}_toePivot_JNT")
                roll_ball_joint = cmds.joint(
                    name=f"{foot_short}_ballPivot_JNT")
                roll_foot_joint = cmds.joint(
                    name=f"{foot_short}_footPivot_JNT")

                heel_loc = cmds.spaceLocator(
                    name=f"{foot_short}_rollPivot_LOC")[0]
                cmds.matchTransform(heel_loc, ik_joint_ball)
                RigHelpers.bake_transform_to_opm(heel_loc)
                cmds.matchTransform(heel_loc, ik_joint_foot,
                                    positionX=True)

                cmds.matchTransform(bank_inner_group, heel_loc)

                cmds.move(0, 0, 4.5 * side_sign, bank_inner_group,
                          relative=True, objectSpace=True)
                cmds.move(0, 0, -10.5 * side_sign, bank_outer_group,
                          relative=True, objectSpace=True)

                cmds.matchTransform(roll_heel_joint, heel_loc)
                cmds.move(-5.0 * side_sign, 0, 0, roll_heel_joint,
                          relative=True, objectSpace=True)

                cmds.matchTransform(roll_toe_joint, ik_joint_ball)
                cmds.move(7.5 * side_sign, 0, 0, roll_toe_joint,
                          relative=True, objectSpace=True)
                cmds.matchTransform(roll_ball_joint, ik_joint_ball)
                cmds.matchTransform(roll_foot_joint, ik_joint_foot)

                pivot_joints = []
                pivot_joints.append(bank_inner_group)
                pivot_joints.append(bank_outer_group)
                pivot_joints.append(roll_heel_joint)
                pivot_joints.append(roll_toe_joint)
                pivot_joints.append(roll_ball_joint)
                pivot_joints.append(roll_foot_joint)

                pivot_joints = cmds.ls(pivot_joints, long=True)
                for joint in pivot_joints:
                    RigHelpers.bake_transform_to_opm(joint)
                RIG_CTX.joint_registry.setdefault(
                    "foot_pivot", {})[f"{limb_name}_{side}"] = pivot_joints

                cmds.delete(heel_loc)

    @staticmethod
    def build_roll_bank_iK_driver():

        schema = UE5_SCHEMA.get("foot", {})

        ik_ctrls = RIG_CTX.control_registry.get("ik", {})

        ik_joints = RIG_CTX.joint_registry.get("ik", {})

        pivot_joints = RIG_CTX.joint_registry.get("foot_pivot", {})
        pivot_groups = RIG_CTX.group_registry.get("foot_pivot", {})

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                foot_short, ball_short = chain
                pivot_chain = pivot_joints.get(f"{limb_name}_{side}")
                pivot_group = pivot_groups.get(f"{limb_name}_{side}")

                ik_ctrl = ik_ctrls.get(foot_short)

                ik_joint_ball = ik_joints.get(ball_short)
                ik_joint_foot = ik_joints.get(foot_short)

                roll_ball_joint = pivot_chain[4]
                roll_foot_joint = pivot_chain[5]

                cmds.addAttr(ik_ctrl, longName="Roll", attributeType="double",
                             defaultValue=0, keyable=True)
                cmds.addAttr(ik_ctrl, longName="Bank", attributeType="double",
                             defaultValue=0, keyable=True)

                foot_ikh = cmds.listRelatives(
                    ik_ctrl, type="ikHandle", fullPath=False)[0]
                ball_ikh = cmds.ikHandle(startJoint=ik_joint_foot,
                                         endEffector=ik_joint_ball,
                                         solver="ikSCsolver",
                                         name=f"{foot_short}_Roll_IKH")[0]

                cmds.parentConstraint(ik_ctrl, pivot_group)

                cmds.parent(ball_ikh, roll_ball_joint)
                cmds.parent(foot_ikh, roll_foot_joint)
                cmds.orientConstraint(roll_foot_joint, ik_joint_foot)

    @staticmethod
    def build_roll_driver():

        schema = UE5_SCHEMA.get("foot", {})

        ik_ctrls = RIG_CTX.control_registry.get("ik", {})

        ik_joints = RIG_CTX.joint_registry.get("ik", {})

        pivot_joints = RIG_CTX.joint_registry.get("foot_pivot", {})

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                foot_short, ball_short = chain
                pivot_chain = pivot_joints.get(f"{limb_name}_{side}")

                ik_ctrl = ik_ctrls.get(foot_short)

                ik_joint_ball = ik_joints.get(ball_short)

                roll_heel_joint = pivot_chain[2]
                roll_toe_joint = pivot_chain[3]
                roll_ball_joint = pivot_chain[4]

                md = cmds.createNode(
                    "multiplyDivide", name=f"{foot_short}_roll_MD")
                cmds.setAttr(f"{md}.input2X", -1.0)
                cmds.setAttr(f"{md}.input2Y", -1.0)
                cmds.setAttr(f"{md}.input2Z", -1.0)

                # stare here

                ball_cond = cmds.createNode(
                    "condition", name=f"{foot_short}_ball_cond")
                cmds.setAttr(f"{ball_cond}.operation", 3)
                cmds.connectAttr(f"{ik_ctrl}.Roll",
                                 f"{ball_cond}.firstTerm")
                cmds.setAttr(f"{ball_cond}.secondTerm", 30)

                cmds.connectAttr(f"{ik_ctrl}.Roll",
                                 f"{ball_cond}.colorIfFalseR")

                clamp = cmds.createNode(
                    "clamp", name=f"{foot_short}_ball_clamp")
                cmds.setAttr(f"{clamp}.minR", 0)
                cmds.setAttr(f"{clamp}.maxR", 30)
                cmds.connectAttr(f"{ball_cond}.outColorR",
                                 f"{clamp}.inputR")
                cmds.connectAttr(f"{clamp}.outputR",
                                 f"{md}.input1X")

                cmds.connectAttr(f"{md}.outputX",
                                 f"{roll_ball_joint}.rotateZ")

                # clamp ball rotation

                pma_rev = cmds.createNode(
                    "plusMinusAverage", name=f"{foot_short}_ball_rev_PMA")
                cmds.setAttr(f"{pma_rev}.operation", 2)
                cmds.setAttr(f"{pma_rev}.input1D[0]", 90)
                cmds.connectAttr(f"{ik_ctrl}.Roll",
                                 f"{pma_rev}.input1D[1]")
                cmds.connectAttr(f"{pma_rev}.output1D",
                                 f"{ball_cond}.colorIfTrueR")

                # reverse ball rotation, input1D[0] = ball rotation returns to 0

                toe_cond = cmds.createNode(
                    "condition", name=f"{foot_short}_toe_cond")
                cmds.setAttr(f"{toe_cond}.operation", 3)
                cmds.connectAttr(f"{ik_ctrl}.Roll",
                                 f"{toe_cond}.firstTerm")
                cmds.setAttr(f"{toe_cond}.secondTerm", 30)
                cmds.setAttr(f"{toe_cond}.colorIfFalseR", 0)

                cmds.connectAttr(f"{ik_ctrl}.Roll",
                                 f"{pma_rev}.input2D[0].input2Dx")
                cmds.setAttr(f"{pma_rev}.input2D[1].input2Dx", 60)

                pma = cmds.createNode("plusMinusAverage",
                                      name=f"{foot_short}_ball_PMA")
                cmds.setAttr(f"{pma}.operation", 1)
                cmds.setAttr(f"{pma}.input1D[1]", 30)
                cmds.connectAttr(f"{pma_rev}.output2Dx",
                                 f"{pma}.input1D[0]")
                cmds.connectAttr(f"{pma}.output1D",
                                 f"{toe_cond}.colorIfTrueR")
                cmds.connectAttr(f"{toe_cond}.outColorR",
                                 f"{md}.input1Y")

                cmds.connectAttr(f"{md}.outputY",
                                 f"{roll_toe_joint}.rotateZ")

                # toe rotation, input2D[1].input2Dx = ball starts to return to 0

                heel_cond = cmds.createNode(
                    "condition", name=f"{foot_short}_heel_cond")
                cmds.setAttr(f"{heel_cond}.operation", 4)
                cmds.connectAttr(f"{ik_ctrl}.Roll",
                                 f"{heel_cond}.firstTerm")
                cmds.setAttr(f"{heel_cond}.secondTerm", 0)
                cmds.setAttr(f"{heel_cond}.colorIfFalseR", 0)
                cmds.connectAttr(f"{ik_ctrl}.Roll",
                                 f"{heel_cond}.colorIfTrueR")
                cmds.connectAttr(f"{heel_cond}.outColorR",
                                 f"{md}.input1Z")

                cmds.connectAttr(f"{md}.outputZ",
                                 f"{roll_heel_joint}.rotateZ")

                # heel rotation

                loc = cmds.spaceLocator(
                    name=f"{foot_short}_ballAimUpRef_LOC")[0]
                cmds.matchTransform(loc, roll_ball_joint)
                cmds.parent(loc, roll_ball_joint)

                side_sign = 1 if side == "l" else -1
                cmds.aimConstraint(roll_toe_joint, ik_joint_ball,
                                   aimVector=(1*side_sign, 0, 0), upVector=(0, 1, 0),
                                   worldUpType="objectrotation", worldUpObject=loc,
                                   worldUpVector=(0, 1, 0))

                # ball aim to toe

    @staticmethod
    def build_bank_driver():

        schema = UE5_SCHEMA.get("foot", {})

        ik_ctrls = RIG_CTX.control_registry.get("ik", {})

        pivot_joints = RIG_CTX.joint_registry.get("foot_pivot", {})

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                pivot_chain = pivot_joints.get(f"{limb_name}_{side}")

                ik_ctrl = ik_ctrls.get(chain[0])

                bank_inner_group = pivot_chain[0]
                bank_outer_group = pivot_chain[1]

                md = cmds.createNode(
                    "multiplyDivide", name=f"{chain[0]}_bank_MD")
                cmds.setAttr(f"{md}.input2X", -1)
                cmds.setAttr(f"{md}.input2Y", -1)

                bank_cond = cmds.createNode(
                    "condition", name=f"{chain[0]}_bank_cond")
                cmds.setAttr(f"{bank_cond}.operation", 5)
                cmds.connectAttr(f"{ik_ctrl}.Bank", f"{bank_cond}.firstTerm")
                cmds.setAttr(f"{bank_cond}.secondTerm", 0)

                cmds.connectAttr(f"{ik_ctrl}.Bank",
                                 f"{bank_cond}.colorIfTrueR")
                cmds.setAttr(f"{bank_cond}.colorIfFalseR", 0)
                cmds.connectAttr(f"{bank_cond}.outColorR",
                                 f"{md}.input1X")
                cmds.connectAttr(f"{md}.outputX",
                                 f"{bank_inner_group}.rotateX")

                cmds.setAttr(f"{bank_cond}.colorIfTrueG", 0)
                cmds.connectAttr(f"{ik_ctrl}.Bank",
                                 f"{bank_cond}.colorIfFalseG")
                cmds.connectAttr(f"{bank_cond}.outColorG",
                                 f"{md}.input1Y")
                cmds.connectAttr(f"{md}.outputY",
                                 f"{bank_outer_group}.rotateX")


class HeadRig:

    @staticmethod
    def build_head_fk_deform_drivers():

        schema = UE5_SCHEMA.get("head", {})

        constraint_system = RigHelpers.get_or_create_group_chain(
            "Group", "driving_system", "constraints")

        fk_ctrls = RIG_CTX.control_registry.get("fk", {})

        deform_joints = RIG_CTX.joint_registry.get("deform", {})

        for side, side_dict in schema.items():

            chain_group = cmds.group(
                empty=True, name=f"constraint_head_{side}_GRP",
                parent=constraint_system)

            for limb_name, chain in side_dict.items():
                for joint_name in chain:

                    fk_ctrl = fk_ctrls.get(joint_name)
                    deform_joint = deform_joints.get(joint_name)

                    constraint = cmds.parentConstraint(
                        fk_ctrl, deform_joint)

                    cmds.parent(constraint, chain_group)


RigHelpers = rig_builders_runtime.RigHelpers
RIG_CTX = rig_builders_runtime.RIG_CTX
UE5_SCHEMA = rig_builders_runtime.UE5_SCHEMA
