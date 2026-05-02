                                          ┌──────────────────────────┐
                                          │        Maya UI Layer     │
                                          │  maya_tools_entry.py     │
                                          │  (PySide / Entry Point)  │
                                          └────────────┬─────────────┘
                                                       │
                                                       ▼
                                    ┌──────────────────────────────────┐
                                    │        Execution Pipeline        │
                                    │  (Triggered by UI Actions)       │
                                    │  Calls: RigBuilder / AnimBuilder │
                                    └──────────────────┬───────────────┘
                                                       │
                             ┌─────────────────────────┼─────────────────────────┐
                             ▼                         ▼                         ▼

          ┌────────────────────────────┐ ┌────────────────────────────┐ ┌────────────────────────────┐
          │        Rig System          │ │     Animation System       │ │      Utility Layer         │
          │────────────────────────────│ │────────────────────────────│ │────────────────────────────│
          │ rig_builders_body.py       │ │ animation_transfer.py      │ │ rig_builders_runtime.py    │
          │ - Skeleton                 │ │ - Retargeting              │ │ - RigHelpers               │
          │                            │ │                            │ │                            │
          │ rig_builders_ctrl.py       │ │ animation_runtime.py       │ │ (Shared Utils)             │
          │ - Controls (FK/IK)         │ │ - FK/IK Transfer           │ │ - Math / Transforms        │
          │                            │ │                            │ │ - Group Management         │
          │ rig_builders_body.py       │ │ animation_locomotion.py    │ │                            │
          │ - Limb (IK/FK)             │ │ - Root Motion              │ │                            │
          │ - Spine                    │ │ - Locomotion               │ │                            │
          │                            │ │ - Foot Lock                │ │                            │
          │ rig_builders_hand_foot.py  │ │                            │ │                            │
          │ - Hand / Foot              │ │                            │ │                            │
          │                            │ │                            │ │                            │
          │ rig_builders_deformation.py│ │                            │ │                            │
          │ - Twist                    │ │                            │ │                            │
          │                            │ │                            │ │                            │
          │ rig_builders_space.py      │ │                            │ │                            │
          │ - Space System             │ │                            │ │                            │
          └───────────────┬────────────┘ └───────────────┬────────────┘ └───────────────┬────────────┘
                          │                              │                              │
                          └──────────────┬───────────────┴──────────────┬───────────────┘
                                         ▼                              ▼
          
                     ┌──────────────────────────────────────────────┐
                     │               Context Layer                  │
                     │                                              │
                     │ rig_builders_runtime.py                      │
                     │  - RIG_CTX                                   │
                     │    • joint_registry                          │
                     │    • control_registry                        │
                     │    • group_registry                          │
                     │                                              │
                     │ animation_runtime.py                         │
                     │  - ANIM_CTX                                  │
                     │    • retarget_registry                       │
                     │    • path_registry                           │
                     │    • locomotion_registry                     │
                     └──────────────────────┬───────────────────────┘
                                            │
                                            ▼
                     ┌──────────────────────────────────────────────┐
                     │            Schema Definition                 │
                     │                                              │
                     │ rig_builders_runtime.py                      │
                     │  - UE5_SCHEMA                                │
                     │    • spine / limbs / hands / twist           │
                     └──────────────────────────────────────────────┘
