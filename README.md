                                          ┌──────────────────────────────────────┐
                                          │            Maya UI Layer             │
                                          │                                      │
                                          │ maya_tools_entry.py                  │
                                          │ - PySide / Maya dockable UI          │
                                          │ - Buttons / user interaction         │
                                          └──────────────────┬───────────────────┘
                                                             │
                                                             ▼
                                          ┌──────────────────────────────────────┐
                                          │         Execution Pipeline           │
                                          │                                      │
                                          │ maya_tools_entry.py                  │
                                          │ - Triggers rig / animation workflows │
                                          │ - Calls RigBuilder / AnimBuilder     │
                                          └──────────────────┬───────────────────┘
                                                             │
                        ┌────────────────────────────────────┼────────────────────────────────────┐
                        ▼                                    ▼                                    ▼
          
          ┌──────────────────────────────┐   ┌──────────────────────────────┐   ┌──────────────────────────────┐
          │          Rig System          │   │       Animation System       │   │      Utility / Helpers       │
          │                              │   │                              │   │                              │
          │ rig_builders_body.py         │   │ animation_transfer.py        │   │ rig_builders_runtime.py      │
          │ - Skeleton                   │   │ - Retargeting                │   │ - RigHelpers                 │
          │ - Limb IK/FK                 │   │ - FK / IK Transfer           │   │ - Scene group utilities      │
          │ - Spine                      │   │ - Root Motion Path           │   │ - Transform helpers          │
          │                              │   │                              │   │                              │
          │ rig_builders_ctrl.py         │   │ animation_locomotion.py      │   │ animation_runtime.py         │
          │ - CtrlFactory                │   │ - Locomotion analysis        │   │ - AnimContext                │
          │ - FK / IK controls           │   │ - Foot Lock                  │   │ - Animhelpers                │
          │ - IK/FK switch controls      │   │ - Motion distance            │   │                              │
          │                              │   │                              │   │                              │
          │ rig_builders_hand_foot.py    │   │ animation_runtime.py         │   │                              │
          │ - Hand curl / spread         │   │ - Animation registries       │   │                              │
          │ - Foot roll / bank           │   │ - Root motion cache data     │   │                              │
          │                              │   │                              │   │                              │
          │ rig_builders_deformation.py  │   │                              │   │                              │
          │ - Twist system               │   │                              │   │                              │
          │ - Twist distribution         │   │                              │   │                              │
          │                              │   │                              │   │                              │
          │ rig_builders_space.py        │   │                              │   │                              │
          │ - Space / follow systems     │   │                              │   │                              │
          └──────────────┬───────────────┘   └──────────────┬───────────────┘   └──────────────┬───────────────┘
                         │                                  │                                  │
                         └──────────────────┬───────────────┴──────────────────┬───────────────┘
                                            ▼                                  ▼
          
                                  ┌────────────────────────────────────────────────────┐
                                  │                  Context Layer                     │
                                  │                                                    │
                                  │ rig_builders_runtime.py                            │
                                  │ - RIG_CTX                                          │
                                  │ - RigBuildContext                                  │
                                  │ - joint_registry                                   │
                                  │ - control_registry                                 │
                                  │ - group_registry                                   │
                                  │                                                    │
                                  │ animation_runtime.py                               │
                                  │ - ANIM_CTX                                         │
                                  │ - AnimContext                                      │
                                  │ - retarget_joint_registry                          │
                                  │ - retarget_time_registry                           │
                                  │ - path_registry                                    │
                                  │ - locomotion_registry                              │
                                  └──────────────────────────┬─────────────────────────┘
                                                             │
                                                             ▼
                                  ┌────────────────────────────────────────────────────┐
                                  │                Schema Definition                   │
                                  │                                                    │
                                  │ rig_builders_runtime.py                            │
                                  │ - UE5_SCHEMA                                       │
                                  │ - spine / limbs / hands / foot / twist             │
                                  └────────────────────────────────────────────────────┘
