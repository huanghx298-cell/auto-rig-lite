

import maya.cmds as cmds

from rig import rig_builders_runtime


class TwistRig:

    @staticmethod
    def build_twist_driver():

        schema = UE5_SCHEMA.get("twist", {})

        twist_system = RigHelpers.get_or_create_group_chain(
            "Group", "driving_system", "TwistSystem")

        deform_joints = RIG_CTX.joint_registry.get("deform", {})

        SIGN_MAP = {
            "upperarm": {"l": -1, "r": 1},
            "lowerarm": {"l": -1, "r": 1},
            "thigh":    {"l": 1,  "r": -1},
            "calf":     {"l": 1,  "r": -1},
        }

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                twist_start_joint = deform_joints.get(f"{limb_name}_{side}")
                twist_end_joint = deform_joints.get(chain[2])

                group = cmds.group(
                    empty=True, name=f"{chain[2]}_twistDriver_GRP", parent=twist_system)

                driver_loc = cmds.spaceLocator(
                    name=f"{chain[2]}_twistDriver_LOC")[0]
                up_vector_loc = cmds.spaceLocator(
                    name=f"{chain[2]}_twistUpVector_LOC")[0]
                cmds.parent(driver_loc, group)
                cmds.parent(up_vector_loc, group)

                cmds.matchTransform(driver_loc, twist_end_joint)
                RigHelpers.bake_transform_to_opm(driver_loc)
                cmds.parentConstraint(
                    twist_end_joint, driver_loc, skipRotate=("x", "y", "z"),
                    maintainOffset=True)

                cmds.matchTransform(up_vector_loc, twist_end_joint)
                cmds.move(0, 0, 5, up_vector_loc,
                          relative=True, objectSpace=True)
                cmds.parentConstraint(
                    twist_end_joint, up_vector_loc, maintainOffset=True)

                side_sign = SIGN_MAP[limb_name][side]
                cmds.aimConstraint(twist_start_joint, driver_loc,
                                   aimVector=(1 * side_sign, 0, 0), upVector=(0, 0, 1),
                                   worldUpType="object", worldUpObject=up_vector_loc)

    @staticmethod
    def build_twist_system():

        schema = UE5_SCHEMA.get("twist", {})

        deform_joints = RIG_CTX.joint_registry.get("deform", {})

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                twist01_joint = deform_joints.get(chain[0])
                twist02_joint = deform_joints.get(chain[1])
                driver_loc = cmds.ls(
                    f"{chain[2]}_twistDriver_LOC", long=True)[0]

                RigHelpers.bake_transform_to_opm(twist01_joint)
                RigHelpers.bake_transform_to_opm(twist02_joint)

                md = cmds.createNode(
                    "multiplyDivide", name=f"{chain[1]}_twistDistribution_MD")
                cmds.setAttr(f"{md}.input2X", 0.33)
                cmds.setAttr(f"{md}.input2Y", 0.66)

                cmds.connectAttr(f"{driver_loc}.rotateX",
                                 f"{md}.input1X")
                cmds.connectAttr(f"{md}.outputX",
                                 f"{twist01_joint}.rotateX")

                cmds.connectAttr(f"{driver_loc}.rotateX",
                                 f"{md}.input1Y")
                cmds.connectAttr(f"{md}.outputY",
                                 f"{twist02_joint}.rotateX")


RigHelpers = rig_builders_runtime.RigHelpers
RIG_CTX = rig_builders_runtime.RIG_CTX
UE5_SCHEMA = rig_builders_runtime.UE5_SCHEMA
