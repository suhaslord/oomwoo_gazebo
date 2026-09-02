# Kitchen world validation checklist

The static check in `scripts/validate_world_assets.py` is only the first gate.
Before proposing the kitchen world upstream, complete all of the runtime/manual
checks below and keep evidence for failures as well as passes.

## 1. Static packaging

```bash
python3 scripts/validate_world_assets.py worlds/kitchen.world
```

Expected: XML parses; all local `model://` and relative asset references resolve;
all visual/collision elements checked by the script contain geometry.

## 2. Gazebo visual pass

Open `worlds/kitchen.world` in the same Gazebo version used by oomwoo and inspect
from human eye level and robot height. Check:

- no missing/pink/black textures;
- believable furniture/appliance scale and placement;
- counters, toe kicks, floor, walls, and obstacles do not visibly overlap;
- no floating or buried assets;
- lighting/exposure is presentable from multiple camera angles.

Save screenshots from at least an overview and robot-height viewpoint.

## 3. Collision pass

Turn on collision visualization and compare visual meshes/primitives against
collision geometry. In particular inspect narrow clearances, toe kicks, table or
counter edges, the refrigerator, and small floor obstacles.

Record and fix any collision that extends materially beyond its visual shape or
allows the robot through a visible solid.

## 4. Robot navigation pass

Launch with the normal oomwoo workflow and drive the vacuum through every major
reachable region. Exercise:

- doorway / narrow-clearance traversal;
- counter toe-kick edges;
- approach to walls and appliances;
- small obstacle avoidance/contact behavior;
- recovery after a near-collision or blocked path.

Do not call the world validated solely because Gazebo loads successfully.

## 5. Upstream-ready evidence

Before opening a PR, include:

- exact Gazebo/ROS 2 versions;
- launch command used;
- static validator output;
- screenshots;
- a short navigation-test result with any known limitations.

This checklist intentionally keeps manual/runtime verification separate from the
static checks so a generated world is never presented as validated without a
human simulation pass.
