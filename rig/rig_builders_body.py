

import maya.cmds as cmds

from rig import rig_builders_runtime


class SkeletonRig:

    @staticmethod
    def register_deform_skeleton(root):

        deform_group = RigHelpers.get_or_create_group_chain(
            "Group", "skeleton", "deform_joints")

        new_root = cmds.parent(root, deform_group)[0]
        new_root = cmds.ls(new_root, long=True)[0]
        RIG_CTX.skeleton_root = new_root

        all_joints = [new_root] + cmds.listRelatives(
            new_root, allDescendents=True, type="joint", fullPath=True)

        for joint in all_joints:
            joint_name = joint.split("|")[-1]
            RIG_CTX.joint_registry.setdefault(
                "deform", {})[joint_name] = joint

    @staticmethod
    def build_limb_ikfk_skeletons():

        SkeletonRig.build_skeleton("limb", "ik")
        SkeletonRig.build_skeleton("limb", "fk")

    @staticmethod
    def build_spine_ikfk_skeletons():

        SkeletonRig.build_skeleton("spine", "ik")
        SkeletonRig.build_skeleton("spine", "fk")

    @staticmethod
    def build_skeleton(category, suffix):

        # print(f"#######################{category}_{suffix}#######################")

        schema = UE5_SCHEMA.get(category, {})

        deform_joints = RIG_CTX.joint_registry.get("deform", {})

        joint_group = RigHelpers.get_or_create_group_chain(
            "Group", "skeleton", f"{suffix}_joints")
        cmds.setAttr(f"{joint_group}.visibility", 0)

        driving_system = RigHelpers.get_or_create_group_chain(
            "Group", "driving_system")
        cmds.setAttr(f"{driving_system}.visibility", 0)

        root_joint = RIG_CTX.skeleton_root
        new_root = cmds.duplicate(root_joint, returnRootsOnly=True)[0]
        new_root = cmds.ls(new_root, long=True)[0]

        all_joints = [new_root] + cmds.listRelatives(
            new_root, allDescendents=True, type="joint", fullPath=True)
        joint_map = {j.split("|")[-1]: j for j in all_joints}

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                base_joint = joint_map.get(chain[0])
                chain_grp = cmds.group(
                    empty=True, name=f"{suffix}_{limb_name}_{side}_jnt_GRP",
                    parent=joint_group)
                chain_grp = cmds.ls(chain_grp, long=True)[0]
                cmds.matchTransform(chain_grp, base_joint)
                RigHelpers.bake_transform_to_opm(chain_grp)
                # cmds.setAttr(f"{chain_grp}.visibility", 0)
                RIG_CTX.group_registry.setdefault(
                    f"{suffix}_joint", {})[f"{limb_name}_{side}"] = chain_grp

                cmds.parent(base_joint, chain_grp)
                chain_root = cmds.listRelatives(
                    chain_grp, children=True, type="joint", fullPath=True)[0]
                chain_joints = [chain_root] + cmds.listRelatives(
                    chain_root, allDescendents=True, type="joint", fullPath=True)
                chain_joints.sort(key=lambda x: x.count("|"), reverse=True)

                keep_set = set(chain)
                rename_queue = []
                for joint in chain_joints:
                    joint_name = joint.split("|")[-1]
                    if joint_name in keep_set:
                        rename_queue.append((joint, joint_name))
                    else:
                        cmds.delete(joint)

                rename_queue.sort(key=lambda x: x[0].count("|"))
                for joint, joint_name in reversed(rename_queue):
                    cmds.rename(joint, f"{joint_name}_{suffix}_JNT")
                for joint, joint_name in rename_queue:
                    new_joint = cmds.ls(
                        f"{joint_name}_{suffix}_JNT", long=True)[0]
                    cmds.setAttr(f"{new_joint}.jointOrient", 0, 0, 0)
                    deform_joint = deform_joints.get(joint_name)
                    cmds.matchTransform(new_joint, deform_joint)
                    RigHelpers.bake_transform_to_opm(new_joint)
                    RIG_CTX.joint_registry.setdefault(
                        suffix, {})[joint_name] = new_joint

        cmds.delete(new_root)


class LimbRig:

    @staticmethod
    def build_limb_ikfk_deform_drivers():

        schema = UE5_SCHEMA.get("limb", {})

        constraint_system = RigHelpers.get_or_create_group_chain(
            "Group", "driving_system", "constraints")

        fk_ctrls = RIG_CTX.control_registry.get("fk", {})
        ik_ctrls = RIG_CTX.control_registry.get("ik", {})
        ikfk_ctrls = RIG_CTX.control_registry.get("ikfk", {})

        fk_joints = RIG_CTX.joint_registry.get("fk", {})
        ik_joints = RIG_CTX.joint_registry.get("ik", {})
        deform_joints = RIG_CTX.joint_registry.get("deform", {})

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                chain_group = cmds.group(
                    empty=True, name=f"constraint_{limb_name}_{side}_GRP",
                    parent=constraint_system)

                ikfk_ctrl = ikfk_ctrls.get(f"{limb_name}_{side}")

                ikfk_ctrl_short = ikfk_ctrl.split("|")[-1]

                md = cmds.createNode(
                    "multiplyDivide", name=f"{ikfk_ctrl_short}_IKFKBlend_MD")
                cmds.setAttr(f"{md}.input2X", 0.1)
                cmds.connectAttr(f"{ikfk_ctrl_short}.IKFKBlend",
                                 f"{md}.input1X")

                rev = cmds.createNode(
                    "reverse", name=f"{ikfk_ctrl_short}_IKFKBlend_REV")
                cmds.connectAttr(f"{md}.outputX",
                                 f"{rev}.inputX")

                for joint_name in chain:

                    fk_joint = fk_joints.get(joint_name)
                    ik_joint = ik_joints.get(joint_name)
                    deform_joint = deform_joints.get(joint_name)

                    fk_ctrl = fk_ctrls.get(joint_name)
                    ik_ctrl = ik_ctrls.get(joint_name)

                    constraint = cmds.parentConstraint(
                        fk_joint, ik_joint, deform_joint)[0]

                    w0_attr = cmds.listAttr(constraint, string="*W0")[0]
                    w1_attr = cmds.listAttr(constraint, string="*W1")[0]

                    cmds.connectAttr(f"{md}.outputX",
                                     f"{constraint}.{w0_attr}")
                    cmds.connectAttr(f"{rev}.outputX",
                                     f"{constraint}.{w1_attr}")

                    if not joint_name.startswith("clavicle"):
                        cmds.connectAttr(f"{md}.outputX",
                                         f"{fk_ctrl}.visibility")
                        if ik_ctrl:
                            cmds.connectAttr(f"{rev}.outputX",
                                             f"{ik_ctrl}.visibility")

                    cmds.parent(constraint, chain_group)

    @staticmethod
    def build_clavicle_fk_ctrl_joint_drivers():

        schema = UE5_SCHEMA.get("limb", {})

        fk_ctrls = RIG_CTX.control_registry.get("fk", {})
        fk_joints = RIG_CTX.joint_registry.get("fk", {})
        ik_joints = RIG_CTX.joint_registry.get("ik", {})

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():
                for joint_name in chain:

                    if not joint_name.startswith("clavicle"):
                        continue

                    fk_ctrl = fk_ctrls.get(joint_name)
                    fk_joint = fk_joints.get(joint_name)
                    ik_joint = ik_joints.get(joint_name)

                    cmds.parentConstraint(fk_ctrl, fk_joint)
                    cmds.parentConstraint(fk_ctrl, ik_joint)

    @staticmethod
    def build_limb_fk_ctrl_joint_drivers():

        schema = UE5_SCHEMA.get("limb", {})

        fk_ctrls = RIG_CTX.control_registry.get("fk", {})
        fk_joints = RIG_CTX.joint_registry.get("fk", {})

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():
                for joint_name in chain:

                    if joint_name.startswith("clavicle"):
                        continue

                    fk_ctrl = fk_ctrls.get(joint_name)
                    fk_joint = fk_joints.get(joint_name)

                    cmds.parentConstraint(fk_ctrl, fk_joint)

    @staticmethod
    def build_limb_ik_ctrl_joint_drivers():

        schema = UE5_SCHEMA.get("limb", {})

        ik_ctrls = RIG_CTX.control_registry.get("ik", {})
        ik_joints = RIG_CTX.joint_registry.get("ik", {})

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                if limb_name == "upperarm":
                    start_i, mid_i, end_i = 1, 2, 3
                else:
                    start_i, mid_i, end_i = 0, 1, 2

                pole_ctrl = ik_ctrls.get(chain[mid_i])
                ik_ctrl = ik_ctrls.get(chain[end_i])

                start_joint = ik_joints.get(chain[start_i])
                end_joint = ik_joints.get(chain[end_i])

                ik_handle = cmds.ikHandle(
                    startJoint=start_joint, endEffector=end_joint,
                    solver="ikRPsolver", name=f"{chain[end_i]}_IKH")[0]
                cmds.poleVectorConstraint(pole_ctrl, ik_handle)
                cmds.parent(ik_handle, ik_ctrl)

                if limb_name == "upperarm":
                    orient_grp = cmds.group(
                        empty=True, name=f"{chain[end_i]}_orient_GRP", parent=ik_ctrl)
                    cmds.matchTransform(orient_grp, end_joint)
                    RigHelpers.bake_transform_to_opm(orient_grp)
                    cmds.orientConstraint(orient_grp, end_joint)


class SpineRig:

    @staticmethod
    def build_spine_ik_curve():

        schema = UE5_SCHEMA.get("spine", {})

        ik_joints = RIG_CTX.joint_registry.get("ik", {})

        spine_system = RigHelpers.get_or_create_group_chain(
            "Group", "driving_system", "spine")

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                points = []
                for joint_name in chain[0:-1]:
                    ik_joint = ik_joints[joint_name]
                    pos = cmds.xform(ik_joint, query=True,
                                     worldSpace=True, translation=True)
                    points.append(pos)

                curve = cmds.curve(
                    editPoint=points, degree=3, name="spine_IK_EP_CRV")

                cmds.parent(curve, spine_system)

    @staticmethod
    def build_spine_curve_driver_joints():

        schema = UE5_SCHEMA.get("spine", {})

        spine_system = RigHelpers.get_or_create_group_chain(
            "Group", "driving_system", "spine")

        ik_joints = RIG_CTX.joint_registry.get("ik", {})

        curve = cmds.ls("spine_IK_EP_CRV", long=True)[0]

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                ref_loc = cmds.spaceLocator(name=f"{limb_name}_MP_ref_LOC")[0]
                deform_loc = cmds.spaceLocator(
                    name=f"{limb_name}_DEF_MP_LOC")[0]

                npoc = cmds.createNode(
                    "nearestPointOnCurve", name=f"{limb_name}_NPC")
                cmds.connectAttr(f"{curve}.worldSpace[0]",
                                 f"{npoc}.inputCurve")
                cmds.connectAttr(f"{deform_loc}.worldPosition[0]",
                                 f"{npoc}.inPosition")

                for i, joint_name in enumerate(chain[0:-1]):

                    driver_jnt = cmds.joint(
                        name=f"{joint_name}_spine_driver_JNT")
                    ik_joint = ik_joints.get(joint_name)

                    cmds.matchTransform(driver_jnt, ref_loc)
                    cmds.parent(driver_jnt, spine_system)
                    RigHelpers.bake_transform_to_opm(driver_jnt)

                    mp = cmds.createNode(
                        "motionPath", name=f"{joint_name}_spine_MP")
                    cmds.connectAttr(f"{curve}.worldSpace[0]",
                                     f"{mp}.geometryPath")
                    cmds.connectAttr(f"{mp}.allCoordinates",
                                     f"{driver_jnt}.translate")

                    cmds.matchTransform(driver_jnt, ik_joint,
                                        position=False, rotation=True, scale=False)

                    cmds.matchTransform(deform_loc, ik_joint)
                    param = cmds.getAttr(f"{npoc}.parameter")
                    cmds.setAttr(f"{mp}.uValue", param)

                cmds.delete(ref_loc, deform_loc, npoc)

                for i in range(1, len(chain[0:-1]) - 1):
                    current = cmds.ls(
                        f"{chain[i]}_spine_driver_JNT", long=True)[0]
                    target = cmds.ls(
                        f"{chain[i + 1]}_spine_driver_JNT", long=True)[0]

                    cmds.aimConstraint(target, current,
                                       aimVector=(1, 0, 0), upVector=(0, 1, 0),
                                       worldUpType="vector",
                                       worldUpVector=(0, 0, -1),)

    @staticmethod
    def build_spine_ik_ctrl_follow_joints():

        schema = UE5_SCHEMA.get("spine", {})

        ik_joints = RIG_CTX.joint_registry.get("ik", {})

        spine_system = RigHelpers.get_or_create_group_chain(
            "Group", "driving_system", "spine")

        curve = cmds.ls("spine_IK_EP_CRV", long=True)[0]

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                start_joint = cmds.joint(name="spine_start_follow_JNT")
                end_joint = cmds.joint(name="spine_end_follow_JNT")

                start_ik = ik_joints[chain[0]]
                end_ik = ik_joints[chain[-2]]
                cmds.parent(start_joint, spine_system)
                cmds.parent(end_joint, spine_system)
                cmds.matchTransform(start_joint, start_ik)
                cmds.matchTransform(end_joint, end_ik)

                mid_info = cmds.createNode(
                    "pointOnCurveInfo", name="spine_mid_POCI")
                cmds.connectAttr(f"{curve}.worldSpace[0]",
                                 f"{mid_info}.inputCurve")
                cmds.setAttr(f"{mid_info}.turnOnPercentage", 1)
                cmds.setAttr(f"{mid_info}.parameter", 0.5)
                mid_pos = cmds.getAttr(f"{mid_info}.position")[0]
                mid_tangent = cmds.getAttr(f"{mid_info}.tangent")[0]
                cmds.delete(mid_info)

                mid_joint = cmds.joint(
                    name="spine_mid_follow_JNT", position=mid_pos)
                cmds.parent(mid_joint, spine_system)

                default_vec = (1, 0, 0)
                rot = cmds.angleBetween(v1=default_vec, v2=mid_tangent,
                                        euler=True)
                cmds.setAttr(f"{mid_joint}.rotateX", -90)
                cmds.setAttr(f"{mid_joint}.rotateY", rot[1])
                cmds.setAttr(f"{mid_joint}.rotateZ", rot[2])

    @staticmethod
    def build_spine_ikfk_deform_drivers():

        schema = UE5_SCHEMA.get("spine", {})

        constraint_system = RigHelpers.get_or_create_group_chain(
            "Group", "driving_system", "constraints")

        fk_ctrls = RIG_CTX.control_registry.get("fk", {})
        ik_ctrls = RIG_CTX.control_registry.get("ik", {})
        ikfk_ctrls = RIG_CTX.control_registry.get("ikfk", {})

        fk_joints = RIG_CTX.joint_registry.get("fk", {})
        ik_joints = RIG_CTX.joint_registry.get("ik", {})
        deform_joints = RIG_CTX.joint_registry.get("deform", {})

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                chain_group = cmds.group(
                    empty=True, name=f"constraint_{limb_name}_{side}_GRP",
                    parent=constraint_system)

                ikfk_ctrl = ikfk_ctrls[f"{limb_name}_{side}"]
                ikfk_ctrl_short = ikfk_ctrl.split("|")[-1]

                md = cmds.createNode(
                    "multiplyDivide", name="spine_c_IKFKBlend_MD")
                cmds.setAttr(f"{md}.input2X", 0.1)
                cmds.connectAttr(f"{ikfk_ctrl_short}.IKFKBlend",
                                 f"{md}.input1X")

                rev = cmds.createNode("reverse", name="spine_c_IKFKBlend_REV")
                cmds.connectAttr(f"{md}.outputX",
                                 f"{rev}.inputX")

                for joint_name in chain:

                    fk_joint = fk_joints[joint_name]
                    ik_joint = ik_joints[joint_name]
                    deform_joint = deform_joints[joint_name]

                    constraint = cmds.parentConstraint(
                        fk_joint, ik_joint, deform_joint)[0]
                    w0_attr = cmds.listAttr(constraint, string="*W0")[0]
                    w1_attr = cmds.listAttr(constraint, string="*W1")[0]
                    cmds.connectAttr(f"{md}.outputX",
                                     f"{constraint}.{w0_attr}")
                    cmds.connectAttr(f"{rev}.outputX",
                                     f"{constraint}.{w1_attr}")

                    fk_ctrl = fk_ctrls[joint_name]
                    cmds.connectAttr(f"{md}.outputX",
                                     f"{fk_ctrl}.visibility")

                    cmds.parent(constraint, chain_group)

                for joint_name in chain[1:4]:
                    ik_ctrl = ik_ctrls.get(joint_name)
                    cmds.connectAttr(f"{rev}.outputX",
                                     f"{ik_ctrl}.visibility")

    @staticmethod
    def build_spine_fk_ctrl_joint_drivers():

        schema = UE5_SCHEMA.get("spine", {})

        fk_ctrls = RIG_CTX.control_registry.get("fk", {})
        fk_joints = RIG_CTX.joint_registry.get("fk", {})

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():
                for joint_name in chain[1:]:

                    fk_ctrl = fk_ctrls.get(joint_name)
                    fk_joint = fk_joints.get(joint_name)

                    cmds.parentConstraint(fk_ctrl, fk_joint)

    @staticmethod
    def build_spine_ik_ctrl_curve_drivers():

        schema = UE5_SCHEMA.get("spine", {})

        ik_ctrls = RIG_CTX.control_registry.get("ik", {})
        ik_groups = RIG_CTX.group_registry.get("ik_ctrl", {})

        start_joint = cmds.ls("spine_start_follow_JNT", long=True)[0]
        mid_joint = cmds.ls("spine_mid_follow_JNT", long=True)[0]
        end_joint = cmds.ls("spine_end_follow_JNT", long=True)[0]

        curve = cmds.ls("spine_IK_EP_CRV", long=True)[0]

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                chain_grp = ik_groups.get(f"{limb_name}_{side}")

                follow_joints = [start_joint, mid_joint, end_joint]
                targets = chain[1:4]
                for joint_name, follow_joint in zip(targets, follow_joints):

                    ctrl_grp = cmds.group(empty=True, name=f"{joint_name}_ik_ctrl_GRP",
                                          world=True)
                    cmds.matchTransform(ctrl_grp, follow_joint)
                    cmds.makeIdentity(ctrl_grp, apply=True, rotate=True)
                    cmds.parent(ctrl_grp, chain_grp)
                    RigHelpers.bake_transform_to_opm(ctrl_grp)

                    ik_ctrl = ik_ctrls.get(joint_name)
                    cmds.matchTransform(ik_ctrl, follow_joint)
                    cmds.makeIdentity(ik_ctrl, apply=True, rotate=True)
                    ik_ctrl = cmds.parent(ik_ctrl, ctrl_grp)[0]
                    ik_ctrl = cmds.ls(ik_ctrl, long=True)[0]
                    RIG_CTX.control_registry.setdefault(
                        "ik", {})[joint_name] = ik_ctrl

                    cmds.makeIdentity(follow_joint, apply=False, rotate=True)
                    RigHelpers.bake_transform_to_opm(follow_joint)

                    cmds.parentConstraint(ik_ctrl, follow_joint)

                cmds.skinCluster(follow_joints, curve, toSelectedBones=True,
                                 maximumInfluences=1, normalizeWeights=1,
                                 name="spine_curve_skinCluster")[0]

    @staticmethod
    def build_spine_ik_ctrl_curve_orient_drivers():

        schema = UE5_SCHEMA.get("spine", {})

        ik_ctrls = RIG_CTX.control_registry.get("ik", {})

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                start_ctrl = ik_ctrls.get(chain[1])
                end_ctrl = ik_ctrls.get(chain[3])

                start_driver_joint = cmds.ls(
                    f"{chain[0]}_spine_driver_JNT", long=True)[0]

                end_driver_joint = cmds.ls(
                    f"{chain[-2]}_spine_driver_JNT", long=True)[0]

                cmds.orientConstraint(
                    start_ctrl, start_driver_joint, maintainOffset=True)
                cmds.orientConstraint(
                    end_ctrl, end_driver_joint, maintainOffset=True)

                mid_ctrl = ik_ctrls.get(chain[2])
                mid_driver_names = [chain[2], chain[3]]

                for joint_name in mid_driver_names:

                    driver = cmds.ls(
                        f"{joint_name}_spine_driver_JNT", long=True)[0]
                    aim_constraints = cmds.listRelatives(
                        driver, type="aimConstraint", fullPath=True)[0]

                    cmds.connectAttr(f"{mid_ctrl}.rotateY",
                                     f"{aim_constraints}.offsetX")

    @staticmethod
    def build_spine_curve_ik_joint_drivers():

        schema = UE5_SCHEMA.get("spine", {})

        ik_joints = RIG_CTX.joint_registry.get("ik", {})

        for side, side_dict in schema.items():
            for limb_name, chain in side_dict.items():

                for joint_name in chain[0:-1]:

                    driver_joint = cmds.ls(
                        f"{joint_name}_spine_driver_JNT", long=True)[0]
                    ik_joint = ik_joints.get(joint_name)

                    cmds.parentConstraint(driver_joint, ik_joint)

    @staticmethod
    def build_spine_hip_ctrl_drivers():

        pelvis_fk_joint = RIG_CTX.joint_registry.get("fk", {}).get("pelvis")
        pelvis_fk_ctrl = RIG_CTX.control_registry.get("fk", {}).get("pelvis")

        hip_ctrl = cmds.ls("pelvis_hip_CTRL", long=True)[0]
        hip_offset_grp = cmds.ls("pelvis_hip_offset_GRP", long=True)[0]
        spine_01_grp = cmds.ls("spine_01_hipFollow_GRP", long=True)[0]
        pelvis_follow_grp = cmds.ls("pelvis_hipFollow_GRP", long=True)[0]

        cmds.parentConstraint(hip_offset_grp, spine_01_grp,
                              skipTranslate=("x", "y", "z"))
        cmds.parentConstraint(pelvis_fk_ctrl, spine_01_grp,
                              skipRotate=("x", "y", "z"), maintainOffset=True)
        cmds.parentConstraint(pelvis_follow_grp, pelvis_fk_joint)


RigHelpers = rig_builders_runtime.RigHelpers
RIG_CTX = rig_builders_runtime.RIG_CTX
UE5_SCHEMA = rig_builders_runtime.UE5_SCHEMA
