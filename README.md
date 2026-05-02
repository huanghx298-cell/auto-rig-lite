                                  ┌──────────────────────────┐
                                  │        Maya UI Layer     │
                                  │  (PySide / Entry Point)  │
                                  └────────────┬─────────────┘
                                               │
                                               ▼
                                  ┌──────────────────────────┐
                                  │    Execution Pipeline    │
                                  │  (Triggered by Actions)  │
                                  └────────────┬─────────────┘
                                               │
                ┌──────────────────────────────┼──────────────────────────────┐
                ▼                              ▼                              ▼

        ┌────────────────────┐     ┌────────────────────┐     ┌────────────────────┐
        │     Rig System     │     │  Animation System  │     │   Utility Layer    │
        │────────────────────│     │────────────────────│     │────────────────────│
        │ - Skeleton         │     │ - Retargeting      │     │ - RigHelpers       │
        │ - Limb (IK/FK)     │     │ - FK/IK Transfer   │     │ - Math / Transform │
        │ - Spine            │     │ - Root Motion      │     │ - Group Utilities  │
        │ - Hand / Foot      │     │ - Locomotion       │     │                    │
        │ - Twist            │     │ - Foot Lock        │     │                    │
        │ - Space System     │     │                    │     │                    │
        └─────────┬──────────┘     └─────────┬──────────┘     └─────────┬──────────┘
                  │                          │                          │
                  └──────────────┬───────────┴──────────────┬───────────┘
                                 ▼                          ▼
        
                   ┌────────────────────────────────────────────┐
                   │               Context Layer                │
                   │                                            │
                   │  RIG_CTX                                   │
                   │   - joint_registry                         │
                   │   - control_registry                       │
                   │   - group_registry                         │
                   │                                            │
                   │  ANIM_CTX                                  │
                   │   - retarget_registry                      │
                   │   - path_registry                          │
                   │   - locomotion_registry                    │
                   └───────────────────┬────────────────────────┘
                                       │
                                       ▼
                   ┌────────────────────────────────────────────┐
                   │             Schema Definition              │
                   │                                            │
                   │               UE5_SCHEMA                   │
                   │   - spine / limbs / hands / twist          │
                   └────────────────────────────────────────────┘
