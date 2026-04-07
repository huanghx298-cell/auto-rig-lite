

import maya.cmds as cmds


UE5_SCHEMA = {

    "head": {
        "c": {
            "head": ("neck_01", "neck_02", "head")
        }
    },

    "spine": {
        "c": {
            "spine": ("pelvis", "spine_01", "spine_02", "spine_03", "spine_04", "spine_05")
        }
    },

    "limb": {
        "l": {
            "upperarm": ("clavicle_l", "upperarm_l", "lowerarm_l", "hand_l"),
            "thigh":    ("thigh_l", "calf_l", "foot_l", "ball_l"),
        },
        "r": {
            "upperarm": ("clavicle_r", "upperarm_r", "lowerarm_r", "hand_r"),
            "thigh":    ("thigh_r", "calf_r", "foot_r", "ball_r"),
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

    "foot": {
        "l": {
            "foot": ("foot_l", "ball_l"),
        },
        "r": {
            "foot": ("foot_r", "ball_r"),
        }
    },

    "twist": {
        "l": {
            "upperarm": ("upperarm_twist_01_l", "upperarm_twist_02_l", "lowerarm_l"),
            "lowerarm": ("lowerarm_twist_02_l", "lowerarm_twist_01_l", "hand_l"),
            "thigh":    ("thigh_twist_01_l", "thigh_twist_02_l", "calf_l"),
            "calf":     ("calf_twist_02_l", "calf_twist_01_l", "foot_l"),
        },
        "r": {
            "upperarm": ("upperarm_twist_01_r", "upperarm_twist_02_r", "lowerarm_r"),
            "lowerarm": ("lowerarm_twist_02_r", "lowerarm_twist_01_r", "hand_r"),
            "thigh":    ("thigh_twist_01_r", "thigh_twist_02_r", "calf_r"),
            "calf":     ("calf_twist_02_r", "calf_twist_01_r", "foot_r"),
        },
    },

}


class RigBuildContext:

    def __init__(self):
        self.skeleton_root = None
        self.control_registry = {}
        self.joint_registry = {}
        self.group_registry = {}

    def clear(self):
        self.skeleton_root = None
        self.control_registry = {}
        self.joint_registry = {}
        self.group_registry = {}

    def rebuild(self):

        self.control_registry = {}

        fk_ctrls_group = cmds.ls("FKSystem", long=True)[0]
        ik_ctrls_group = cmds.ls("IKSystem", long=True)[0]
        ikfk_ctrls_group = cmds.ls("IKFKSystem", long=True)[0]

        fk_ctrls = cmds.listRelatives(
            fk_ctrls_group, allDescendents=True, type="transform", fullPath=True)
        ik_ctrls = cmds.listRelatives(
            ik_ctrls_group, allDescendents=True, type="transform", fullPath=True)
        ikfk_ctrls = cmds.listRelatives(
            ikfk_ctrls_group, allDescendents=True, type="transform", fullPath=True)

        for node in fk_ctrls:
            name = node.split("|")[-1]
            if name.endswith("_fk_CTRL"):
                joint = name[:-8]
                self.control_registry.setdefault("fk", {})[joint] = node
        for node in ik_ctrls:
            name = node.split("|")[-1]
            if name.endswith("_ik_CTRL"):
                joint = name[:-8]
                self.control_registry.setdefault("ik", {})[joint] = node
            elif name.endswith("_pole_CTRL"):
                joint = name[:-10]
                self.control_registry.setdefault("ik", {})[joint] = node
        for node in ikfk_ctrls:
            name = node.split("|")[-1]
            if name.endswith("_ikfk_CTRL"):
                key = name[:-10]
                self.control_registry.setdefault("ikfk", {})[key] = node


class RigHelpers:

    @staticmethod
    def create_joint(name, parent, match_target):

        cmds.select(clear=True)

        joint = cmds.joint(n=name)
        cmds.parent(joint, parent)
        cmds.matchTransform(joint, match_target)
        RigHelpers.bake_transform_to_opm(joint)

        cmds.setAttr(joint + ".jointOrient", 0, 0, 0)

        cmds.select(clear=True)

        return joint

    @staticmethod
    def get_or_create_group_chain(*names):

        parent = None
        for name in names:
            if cmds.objExists(name):
                node = name
            else:
                if parent is None:
                    node = cmds.group(empty=True, name=name)
                else:
                    node = cmds.group(empty=True, name=name, parent=parent)

            parent = node

        return parent

    @staticmethod
    def bake_transform_to_opm(node):

        m = cmds.xform(node, q=True, m=True, os=True)
        old_opm = cmds.getAttr(node + ".offsetParentMatrix")

        new_m = [0] * 16

        for row in range(4):
            for col in range(4):
                new_m[row * 4 + col] = sum(
                    m[row * 4 + k] * old_opm[k * 4 + col]for k in range(4))

        cmds.setAttr(node + ".offsetParentMatrix",
                     *new_m, type="matrix")

        cmds.setAttr(node + ".translate", 0, 0, 0)
        cmds.setAttr(node + ".rotate", 0, 0, 0)
        cmds.setAttr(node + ".scale", 1, 1, 1)

    @staticmethod
    def bake_opm_to_transform(node):

        local_m = cmds.xform(node, q=True, m=True, os=True)
        opm = cmds.getAttr(node + ".offsetParentMatrix")

        baked = [0] * 16
        for row in range(4):
            for col in range(4):
                baked[row * 4 + col] = sum(
                    local_m[row * 4 + k] * opm[k * 4 + col]
                    for k in range(4)
                )

        dcm = cmds.createNode("decomposeMatrix", n="__opmBake_DCM__")
        cmds.setAttr(dcm + ".inputMatrix", *baked, type="matrix")

        t = cmds.getAttr(dcm + ".outputTranslate")[0]
        r = cmds.getAttr(dcm + ".outputRotate")[0]
        s = cmds.getAttr(dcm + ".outputScale")[0]
        sh = cmds.getAttr(dcm + ".outputShear")[0]

        cmds.delete(dcm)

        identity = [1, 0, 0, 0,
                    0, 1, 0, 0,
                    0, 0, 1, 0,
                    0, 0, 0, 1]
        cmds.setAttr(node + ".offsetParentMatrix",
                     *identity, type="matrix")

        cmds.setAttr(node + ".translate", *t)
        cmds.setAttr(node + ".rotate", *r)
        cmds.setAttr(node + ".scale", *s)
        cmds.setAttr(node + ".shear", *sh)

    @staticmethod
    def bake_joint_to_attributes(joint):

        world_mtx = cmds.xform(joint, q=True, m=True, ws=True)

        cmds.setAttr(joint + ".offsetParentMatrix",
                     *([1, 0, 0, 0,
                        0, 1, 0, 0,
                        0, 0, 1, 0,
                        0, 0, 0, 1]), type="matrix")

        cmds.setAttr(joint + ".jointOrient", 0, 0, 0)

        cmds.xform(joint, m=world_mtx, ws=True)

    @staticmethod
    def create_group_parented_matched(name, parent, match):

        grp = cmds.group(empty=True, name=name, parent=parent)
        cmds.matchTransform(grp, match)
        RigHelpers.bake_transform_to_opm(grp)

        return grp


RIG_CTX = RigBuildContext()
