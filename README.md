                          ┌──────────────────────────┐
                          │        Maya UI Layer     │
                          │  (PySide / Entry Point)  │
                          │  - Buttons / Tools       │
                          │  - User Interaction      │
                          └────────────┬─────────────┘
                                       │
                                       ▼
                     ┌──────────────────────────────────┐
                     │        Execution Pipeline        │
                     │  (Triggered by UI Actions)       │
                     └────────────┬─────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        ▼                         ▼                         ▼

┌──────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
│    Rig System    │   │   Animation System   │   │   Utility / Helpers  │
│                  │   │                      │   │                      │
│ - Skeleton       │   │ - Retargeting        │   │ - RigHelpers         │
│ - Limb (IK/FK)   │   │ - FK / IK Transfer   │   │ - Math / Transforms  │
│ - Spine          │   │ - Root Motion        │   │ - Group Management   │
│ - Hand / Foot    │   │ - Locomotion         │   │                      │
│ - Twist          │   │ - Foot Lock          │   │                      │
│ - Space System   │   │                      │   │                      │
└─────────┬────────┘   └──────────┬───────────┘   └──────────┬───────────┘
          │                       │                          │
          └──────────────┬────────┴──────────────┬───────────┘
                         ▼                       ▼

           ┌──────────────────────────────┐
           │        Context Layer         │
           │                              │
           │  RIG_CTX                     │
           │   - joint_registry           │
           │   - control_registry         │
           │   - group_registry           │
           │                              │
           │  ANIM_CTX                    │
           │   - retarget_registry        │
           │   - path_registry            │
           │   - locomotion_registry      │
           └────────────┬─────────────────┘
                        │
                        ▼
           ┌──────────────────────────────┐
           │      Schema Definition       │
           │                              │
           │        UE5_SCHEMA            │
           │                              │
           │  - spine                     │
           │  - limbs                     │
           │  - hands                     │
           │  - twist                     │
           └──────────────────────────────┘
