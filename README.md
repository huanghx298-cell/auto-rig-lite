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
┌────────────────────┐     ┌────────────────────┐    
│     Rig System     │     │  Animation System  │    
│────────────────────│     │────────────────────│     
│ - Skeleton         │     │ - Retargeting      │    
│ - Limb (IK/FK)     │     │ - FK/IK Transfer   │   
│ - Spine            │     │ - Root Motion      │    
│ - Hand / Foot      │     │ - Locomotion       │   
│ - Twist            │     │ - Foot Lock        │    
│ - Space System     │     │                    │    
└─────────┬──────────┘     └─────────┬──────────┘     
          │                          │                
          └──────────────┬───────────┴
                         ▼                         
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
