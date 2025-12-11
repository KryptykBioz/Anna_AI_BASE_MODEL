# Complete Minecraft Guide for AI Gaming Agent

## Introduction to Minecraft

Minecraft is a 3D voxel-based sandbox game where you control a character in a procedurally generated world made entirely of cubic blocks. Your goal is to survive, gather resources, craft tools, build structures, and progress through increasingly difficult challenges.

**Core Concept**: Everything in the world is made of blocks that can be broken and placed. You transform raw materials into useful items through crafting and smelting.

## Understanding the Game World

### Block-Based Environment

The entire world consists of 1×1×1 meter cubes called blocks. Each block type has different properties:

- **Solid Blocks**: Cannot pass through (stone, dirt, wood)
- **Transparent Blocks**: Can see through (glass, leaves)
- **Fluid Blocks**: Can pass through but slows movement (water, lava)
- **Air Blocks**: Empty space you can move through

### World Dimensions

The world is infinite horizontally but limited vertically:
- **Build Height**: Y=-64 (bedrock floor) to Y=320 (sky limit)
- **Sea Level**: Y=64 (standard water level)
- **Surface**: Y=60-80 (varies by biome)

### Coordinate System

Navigation uses a 3D coordinate system:
- **X-axis**: East (+) / West (-)
- **Y-axis**: Up (+) / Down (-)
- **Z-axis**: South (+) / North (-)

Always track your home base coordinates to avoid getting lost.

### Time and Day/Night Cycle

- **Full Day**: 20 real-world minutes
- **Daytime**: 10 minutes (safe for surface activity)
- **Nighttime**: 7 minutes (hostile mobs spawn)
- **Twilight**: 3 minutes (dawn/dusk transitions)

**Critical**: Hostile mobs spawn in darkness and despawn in sunlight. Plan activities around this cycle.

## Biomes and Terrain Types

Biomes are distinct geographical regions with unique resources and characteristics:

### Forest Biomes
- **Appearance**: Dense trees (oak, birch, dark oak)
- **Resources**: Wood, saplings, mushrooms, flowers
- **Mobs**: Passive animals (pigs, cows, chickens)
- **Advantages**: Abundant wood for early game

### Plains Biomes
- **Appearance**: Flat grassland with scattered trees
- **Resources**: Grass, flowers, occasional trees
- **Mobs**: Horses, passive animals, villages (common)
- **Advantages**: Easy to navigate and build

### Mountain Biomes
- **Appearance**: Tall stone peaks, steep cliffs
- **Resources**: Stone, coal, iron, emeralds
- **Mobs**: Goats, standard hostile mobs
- **Advantages**: High ore concentration, good visibility

### Desert Biomes
- **Appearance**: Sand dunes, sandstone, cacti
- **Resources**: Sand, sandstone, dead bushes
- **Structures**: Villages, temples, wells
- **Dangers**: No wood, no water, husks (desert zombies)

### Ocean Biomes
- **Appearance**: Deep water bodies
- **Resources**: Fish, kelp, sea grass, coral
- **Structures**: Shipwrecks, ocean monuments, ruins
- **Dangers**: Drowning, drowned mobs

### Cave Systems
- **Appearance**: Underground tunnels and caverns
- **Resources**: All ores, underground lakes, minerals
- **Structures**: Dungeons, mineshafts, amethyst geodes
- **Dangers**: Hostile mobs, fall damage, lava pools

### Swamp Biomes
- **Appearance**: Shallow water, vines, lily pads
- **Resources**: Clay, slime balls, witch huts
- **Mobs**: Slimes, witches, standard mobs
- **Advantages**: Clay for bricks, slime for redstone

## Understanding Your Character

### Player Stats

Your character has three visible stats:

**Health (Hearts)**
- **Maximum**: 20 HP (10 hearts displayed)
- **Regeneration**: Automatic when hunger > 18/20
- **Loss**: Combat, falling, drowning, starvation, fire, lava

**Hunger (Food Bar)**
- **Maximum**: 20 points (10 drumsticks displayed)
- **Depletion**: Sprinting, jumping, combat, healing
- **Effects**: 
  - 18-20: Health regenerates
  - 6-17: Normal function, no regeneration
  - 1-5: Cannot sprint
  - 0: Health loss (starvation damage)

**Experience (XP Bar)**
- **Gained**: Mining ores, killing mobs, breeding, fishing, smelting
- **Used**: Enchanting items, repairing tools at anvil
- **Levels**: Accumulate to unlock better enchantments

### Movement Capabilities

**Walking**: Standard speed, no hunger cost
**Sprinting**: 30% faster, depletes hunger quickly
**Jumping**: Clear 1-block height, costs hunger while sprinting
**Crouching**: Prevents falling off edges, silent movement, slow
**Swimming**: Move through water, need to surface for air
**Climbing**: Ladders and vines allow vertical movement

### Inventory System

**Inventory Slots**: 36 total
- **Main Inventory**: 27 slots (3×9 grid)
- **Hotbar**: 9 slots (quick access, numbered 1-9)
- **Armor Slots**: 4 slots (helmet, chestplate, leggings, boots)
- **Offhand Slot**: 1 slot (shields, torches, blocks)

**Stack Sizes**:
- Most blocks: 64 per stack
- Ender pearls, snowballs, eggs: 16 per stack
- Tools, weapons, armor: 1 per stack (don't stack)

## Block Types and Properties

### Natural Blocks

**Dirt**
- **Breaking Speed**: Fast (bare hands: 0.75s, shovel: faster)
- **Tool**: Shovel (optional but faster)
- **Drops**: Dirt block
- **Uses**: Farming (converts to farmland), building, landscaping

**Stone**
- **Breaking Speed**: Slow (bare hands: impossible, pickaxe required)
- **Tool**: Pickaxe (wooden or better)
- **Drops**: Cobblestone (unless silk touch enchanted)
- **Uses**: Tools, building, smelting into smooth stone

**Wood (Logs)**
- **Breaking Speed**: Medium (bare hands: 3s, axe: faster)
- **Tool**: Axe (optional but much faster)
- **Drops**: Log block
- **Uses**: Crafting planks (primary early-game resource)

**Sand**
- **Breaking Speed**: Fast (bare hands: 0.75s, shovel: faster)
- **Tool**: Shovel (optional)
- **Drops**: Sand
- **Special**: Falls when unsupported (gravity block)
- **Uses**: Glass crafting, concrete, building

**Gravel**
- **Breaking Speed**: Fast (bare hands: 0.9s, shovel: faster)
- **Tool**: Shovel (optional)
- **Drops**: Gravel (90%), flint (10%)
- **Special**: Falls when unsupported (gravity block)
- **Uses**: Concrete, paths, flint for arrows

**Coal Ore**
- **Breaking Speed**: Medium
- **Tool**: Pickaxe (wooden or better) - required
- **Drops**: Coal (1-2 pieces)
- **Uses**: Fuel, torches, essential early resource
- **Location**: Y=0 to Y=192 (common at all levels)

**Iron Ore**
- **Breaking Speed**: Medium
- **Tool**: Pickaxe (stone or better) - required
- **Drops**: Raw iron (must smelt into ingots)
- **Uses**: Tools, armor, buckets, rails - mid-game essential
- **Location**: Y=-64 to Y=256 (most common Y=16)

**Gold Ore**
- **Breaking Speed**: Medium
- **Tool**: Pickaxe (iron or better) - required
- **Drops**: Raw gold (must smelt into ingots)
- **Uses**: Powered rails, golden apples, piglins
- **Location**: Y=-64 to Y=32 (most common Y=-16)

**Diamond Ore**
- **Breaking Speed**: Slow
- **Tool**: Pickaxe (iron or better) - required
- **Drops**: Diamond (1 piece)
- **Uses**: Best tools and armor, enchanting table
- **Location**: Y=-64 to Y=16 (most common Y=-59)

**Redstone Ore**
- **Breaking Speed**: Medium
- **Tool**: Pickaxe (iron or better) - required
- **Drops**: Redstone dust (4-5 pieces)
- **Uses**: Circuits, mechanisms, brewing
- **Location**: Y=-64 to Y=16
- **Special**: Glows when walked on

### Constructed Blocks

**Cobblestone**
- **Source**: Mining stone blocks
- **Uses**: Tools, furnace, building (blast-resistant)
- **Properties**: Fire-proof, explosion-resistant

**Wood Planks**
- **Source**: Crafting logs (1 log = 4 planks)
- **Uses**: Tools, crafting table, building
- **Properties**: Flammable, multiple color variants

**Glass**
- **Source**: Smelting sand
- **Properties**: Transparent, fragile (breaks without drops unless silk touch)
- **Uses**: Windows, greenhouses, decorative

**Bricks**
- **Source**: Smelting clay, crafting into blocks
- **Properties**: Decorative, fire-proof
- **Uses**: Building, aesthetics

### Functional Blocks

**Crafting Table**
- **Recipe**: 4 wood planks (2×2)
- **Function**: Enables 3×3 crafting recipes
- **Usage**: Right-click to open crafting interface
- **Essential**: First item to craft after gathering wood

**Furnace**
- **Recipe**: 8 cobblestone (hollow square)
- **Function**: Smelts ores, cooks food
- **Usage**: Place fuel in bottom, item to smelt on top
- **Essential**: Required for processing iron, gold, and cooking

**Chest**
- **Recipe**: 8 wood planks (hollow square)
- **Function**: Stores 27 items
- **Usage**: Right-click to open, shift-click for quick transfer
- **Special**: Two chests side-by-side create large chest (54 slots)

**Bed**
- **Recipe**: 3 wool + 3 wood planks
- **Function**: Skip night, set respawn point
- **Usage**: Right-click at night (explodes in Nether/End)
- **Critical**: Always have a bed to avoid losing progress

**Door**
- **Recipe**: 6 wood planks (2×3)
- **Function**: Controlled passage through walls
- **Types**: Wooden (opens by hand), iron (needs redstone)

**Torch**
- **Recipe**: 1 coal/charcoal + 1 stick
- **Function**: Provides light (level 14)
- **Usage**: Place on walls or floors
- **Critical**: Prevents mob spawning in lit areas

### Interactive Blocks

**Soil Types**:
- **Grass Block**: Natural surface, converts to dirt when mined
- **Dirt**: Basic earth block, can be tilled for farming
- **Farmland**: Created by hoeing dirt near water, grows crops
- **Mycelium**: Found in mushroom biomes, spreads mushrooms

**Water**
- **Properties**: Flows up to 7 blocks horizontally from source
- **Effects**: Slows movement, prevents fall damage
- **Uses**: Farming, transportation, mob barriers, safety

**Lava**
- **Properties**: Flows 3 blocks horizontally (overworld)
- **Effects**: Instant death unless fire resistance, destroys items
- **Uses**: Trash disposal, mob killer, fuel source (bucket)
- **Danger**: Extremely hazardous - avoid contact

## Tool System

### Tool Categories

**Pickaxe** (Most Important)
- **Purpose**: Mine stone, ores, and mineral blocks
- **Required For**: Stone, coal, iron, gold, diamond, redstone
- **Speed**: Different materials mine at different speeds
- **Without Correct Tool**: Block breaks but drops nothing

**Axe**
- **Purpose**: Chop wood and wooden items efficiently
- **Optional For**: Wood can be broken by hand
- **Bonus**: Faster than hands (5x with iron axe)
- **Combat**: Can be used as weapon (more damage, slower)

**Shovel**
- **Purpose**: Dig dirt, sand, gravel, and snow quickly
- **Optional For**: These blocks can be broken by hand
- **Special**: Creates grass paths (aesthetic)

**Hoe**
- **Purpose**: Till dirt into farmland for crops
- **Required For**: Agriculture and farming
- **Bonus**: Harvests hay bales, leaves, and nether wart faster

**Sword**
- **Purpose**: Combat weapon
- **Damage**: Higher than other tools
- **Speed**: Faster attack speed than axes
- **Durability**: More durable when fighting

### Tool Material Tiers

**Wooden Tools** (First Tier)
- **Materials**: 2 sticks + 3 wood planks
- **Mining Speed**: 2x hand speed
- **Durability**: 59 uses
- **Can Mine**: Wood, dirt, crops, stone (stone only)
- **When**: Immediately after gathering wood

**Stone Tools** (Second Tier)
- **Materials**: 2 sticks + 3 cobblestone
- **Mining Speed**: 4x hand speed
- **Durability**: 131 uses
- **Can Mine**: All wood tier + iron ore, lapis
- **When**: After mining first stone

**Iron Tools** (Third Tier)
- **Materials**: 2 sticks + 3 iron ingots
- **Mining Speed**: 6x hand speed
- **Durability**: 250 uses
- **Can Mine**: All stone tier + diamond, gold, redstone
- **When**: After smelting first iron ore

**Diamond Tools** (Fourth Tier)
- **Materials**: 2 sticks + 3 diamonds
- **Mining Speed**: 8x hand speed
- **Durability**: 1,561 uses
- **Can Mine**: All iron tier + obsidian, ancient debris
- **When**: After finding diamonds (major milestone)

**Netherite Tools** (Fifth Tier - Best)
- **Materials**: Diamond tool + netherite ingot (smithing)
- **Mining Speed**: 9x hand speed
- **Durability**: 2,031 uses
- **Special**: Fire/lava proof, doesn't burn
- **When**: Late game, after Nether exploration

### Tool Usage Rules

**Correct Tool = Faster Mining + Item Drops**
- Stone broken with pickaxe = drops cobblestone
- Stone broken with hand = takes 10 seconds, drops nothing

**Durability Management**
- Each block mined = 1 durability lost
- Tool breaks = disappears completely
- **Strategy**: Craft new tool when current has <25% durability

**Tool Efficiency Chart**
| Block Type | Best Tool | Without Tool |
|------------|-----------|--------------|
| Stone/Ore | Pickaxe | No drops |
| Wood | Axe | 5x slower |
| Dirt/Sand | Shovel | 5x slower |
| Crops | Any | Same speed |
| Wool | Shears | 1 wool vs none |

## Crafting System

### Crafting Interfaces

**2×2 Grid (Inventory Crafting)**
- **Access**: Press 'E' or inventory key
- **Recipes**: Basic items (planks, sticks, torches, crafting table)
- **Limitation**: Only 4 slots, limits complexity

**3×3 Grid (Crafting Table)**
- **Access**: Right-click crafting table
- **Recipes**: All items requiring >4 materials
- **Requirement**: Need crafting table for most items

### Essential First Recipes

**Wood Planks** (2×2 Grid)
```
Recipe: 1 wood log anywhere
Output: 4 planks
Pattern: Single log in any slot
```
**Use First**: Most versatile material in early game

**Sticks** (2×2 Grid)
```
Recipe: 2 planks vertically
Output: 4 sticks
Pattern:
[Plank]
[Plank]
```
**Critical Component**: Required for all tools

**Crafting Table** (2×2 Grid)
```
Recipe: 4 planks filling grid
Output: 1 crafting table
Pattern:
[Plank][Plank]
[Plank][Plank]
```
**First Goal**: Craft this immediately after gathering wood

### Tool Crafting Patterns (3×3 Grid)

**Pickaxe Pattern**
```
[Mat][Mat][Mat]
[ ][Stick][ ]
[ ][Stick][ ]
```
Where Mat = Wood Planks, Cobblestone, Iron, Diamond

**Axe Pattern**
```
[Mat][Mat][ ]
[Mat][Stick][ ]
[ ][Stick][ ]
```

**Shovel Pattern**
```
[ ][Mat][ ]
[ ][Stick][ ]
[ ][Stick][ ]
```

**Sword Pattern**
```
[ ][Mat][ ]
[ ][Mat][ ]
[ ][Stick][ ]
```

**Hoe Pattern**
```
[Mat][Mat][ ]
[ ][Stick][ ]
[ ][Stick][ ]
```

### Critical Early Items

**Torch** (Lighting)
```
Recipe: 1 coal/charcoal on top of 1 stick
Output: 4 torches
Importance: Prevents mob spawning
```

**Chest** (Storage)
```
Recipe: 8 planks in hollow square (3×3)
Output: 1 chest
Stores: 27 items
```

**Furnace** (Smelting)
```
Recipe: 8 cobblestone in hollow square
Output: 1 furnace
Function: Smelt ores, cook food
```

**Bed** (Respawn Point)
```
Recipe: 3 wool (top row) + 3 planks (bottom row)
Output: 1 bed
Critical: Sets spawn point, skips night
```

### Armor Crafting (Protection)

**Helmet Pattern**
```
[Mat][Mat][Mat]
[Mat][ ][Mat]
[ ][ ][ ]
```
**Protection**: 2-3 armor points

**Chestplate Pattern**
```
[Mat][ ][Mat]
[Mat][Mat][Mat]
[Mat][Mat][Mat]
```
**Protection**: 5-8 armor points (most important piece)

**Leggings Pattern**
```
[Mat][Mat][Mat]
[Mat][ ][Mat]
[Mat][ ][Mat]
```
**Protection**: 4-6 armor points

**Boots Pattern**
```
[ ][ ][ ]
[Mat][ ][Mat]
[Mat][ ][Mat]
```
**Protection**: 1-3 armor points

**Armor Materials**: Leather < Gold < Chainmail < Iron < Diamond < Netherite

### Smelting System

**How Smelting Works**:
1. Place furnace in world
2. Right-click to open interface
3. Top slot: Item to smelt (ore, food, sand)
4. Bottom slot: Fuel (coal, wood, lava bucket)
5. Output appears in right slot after smelting time

**Common Smelting Recipes**:
| Input | Output | Time |
|-------|--------|------|
| Raw Iron | Iron Ingot | 10 sec |
| Raw Gold | Gold Ingot | 10 sec |
| Sand | Glass | 10 sec |
| Cobblestone | Stone | 10 sec |
| Wood Log | Charcoal | 10 sec |
| Raw Meat | Cooked Meat | 10 sec |
| Clay Ball | Brick | 10 sec |

**Fuel Efficiency**:
| Fuel | Smelts | Duration |
|------|--------|----------|
| Lava Bucket | 100 items | 1000 sec |
| Coal Block | 80 items | 800 sec |
| Coal | 8 items | 80 sec |
| Charcoal | 8 items | 80 sec |
| Wood Plank | 1.5 items | 15 sec |
| Stick | 0.5 items | 5 sec |

**Early Game Fuel**: Use wood until coal is found, then switch to coal

## Mobs (Creatures)

### Passive Mobs (Friendly)

**Cow**
- **Health**: 10 HP
- **Drops**: Leather (0-2), raw beef (1-3)
- **Breeding**: Wheat
- **Special**: Can be milked with bucket
- **Value**: Leather for books, beef for food

**Pig**
- **Health**: 10 HP
- **Drops**: Raw porkchop (1-3)
- **Breeding**: Carrots, potatoes, beetroot
- **Special**: Can be ridden with saddle and carrot on stick
- **Value**: Good food source

**Chicken**
- **Health**: 4 HP
- **Drops**: Feathers (0-2), raw chicken (1)
- **Breeding**: Seeds (wheat, beetroot, melon, pumpkin)
- **Special**: Lays eggs every 5-10 minutes
- **Value**: Feathers for arrows, eggs for baking

**Sheep**
- **Health**: 8 HP
- **Drops**: Wool (1), raw mutton (1-2)
- **Breeding**: Wheat
- **Special**: Can be sheared for wool without killing (regrows)
- **Value**: Wool for beds and decoration

**Horse**
- **Health**: 15-30 HP (varies)
- **Drops**: Leather (0-2)
- **Taming**: Repeatedly ride until hearts appear
- **Special**: Fast transportation with saddle
- **Value**: Travel speed (up to 14.5 m/s)

### Hostile Mobs (Dangerous)

**Zombie**
- **Health**: 20 HP
- **Damage**: 3 (easy) to 5 (hard) per hit
- **Behavior**: Chases player on sight, slow movement
- **Special**: Burns in sunlight, breaks doors on hard difficulty
- **Drops**: Rotten flesh, rarely iron/carrot/potato
- **Strategy**: Fight in daylight or well-lit areas

**Skeleton**
- **Health**: 20 HP
- **Damage**: 2-5 per arrow (distance dependent)
- **Behavior**: Shoots arrows from distance, burns in sunlight
- **Special**: Backs away if player approaches
- **Drops**: Bones, arrows
- **Strategy**: Use cover, rush with shield, or snipe with bow

**Creeper**
- **Health**: 20 HP
- **Damage**: Explosion (4-49 damage based on distance)
- **Behavior**: Silently approaches, hisses before exploding (1.5s)
- **Special**: Destroys blocks, doesn't burn in sunlight
- **Drops**: Gunpowder
- **Strategy**: Hit and back away, or shoot from distance
- **Critical**: Most dangerous mob to structures

**Spider**
- **Health**: 16 HP
- **Damage**: 2-3 per hit
- **Behavior**: Climbs walls, neutral in light (hostile in darkness)
- **Special**: Can fit through 2-block-wide gaps
- **Drops**: String, spider eyes
- **Strategy**: Fight in enclosed spaces, prevent climbing

**Enderman**
- **Health**: 40 HP
- **Damage**: 7-10 per hit
- **Behavior**: Teleports, neutral unless looked at or attacked
- **Special**: Teleports away from projectiles, damaged by water
- **Drops**: Ender pearls (for End portal)
- **Strategy**: Don't look at face (look at legs/body), fight under 3-block ceiling

**Cave Spider**
- **Health**: 12 HP
- **Damage**: 2-3 + poison effect
- **Behavior**: Found near spawners in mineshafts, very aggressive
- **Special**: Smaller hitbox, inflicts poison
- **Drops**: String, spider eyes
- **Strategy**: Block spawner with torches first

**Witch**
- **Health**: 26 HP
- **Damage**: Throws harmful potions
- **Behavior**: Drinks healing potions during combat
- **Special**: Immune to poison, resistant to magic
- **Drops**: Potions, redstone, glowstone, sugar
- **Strategy**: Rush with sword, don't let it heal

### Neutral Mobs (Conditional Hostility)

**Wolf**
- **Health**: 8 HP (wild), 20 HP (tamed)
- **Behavior**: Neutral, attacks if hit
- **Taming**: Feed bones (several required)
- **Tamed Behavior**: Follows owner, attacks owner's targets
- **Value**: Combat companion, sits on command

**Iron Golem**
- **Health**: 100 HP
- **Damage**: 7-21 per hit
- **Behavior**: Protects villagers, hostile if player attacks
- **Special**: High knockback, can't be killed easily
- **Drops**: Iron ingots (3-5), poppies
- **Strategy**: Avoid aggression near villages

**Zombie Pigman (Zombified Piglin)**
- **Health**: 20 HP
- **Behavior**: Neutral in Nether, hostile if one is attacked
- **Special**: Entire group becomes hostile if any are hurt
- **Strategy**: Avoid combat unless necessary, area attack dangerous

### Boss Mobs

**Ender Dragon**
- **Health**: 200 HP
- **Location**: The End dimension
- **Behavior**: Flies around, destroys blocks, shoots fireballs
- **Defeat**: Destroy end crystals first, attack with bow and sword
- **Reward**: Dragon egg, massive XP, End gateway access

**Wither**
- **Health**: 300 HP (600 on Bedrock)
- **Summoning**: T-shape with soul sand and 3 wither skeleton skulls
- **Behavior**: Flies, shoots explosive skulls, wither effect
- **Reward**: Nether star (for beacon crafting)

## Food and Hunger System

### Hunger Mechanics

**Hunger Depletion**:
- **Sprinting**: 0.1 hunger per meter
- **Jumping while sprinting**: 0.2 per jump
- **Swimming**: 0.01 per meter
- **Combat**: 0.1 per hit given
- **Healing**: 6 hunger to heal 1 HP

**Saturation** (Hidden Stat):
- Acts as hunger buffer
- Depletes before visible hunger bar
- Better food = more saturation
- Explains why hunger drops faster after eating low-quality food

### Food Quality Comparison

**Best Foods** (Efficiency):
| Food | Hunger | Saturation | How to Obtain |
|------|--------|------------|---------------|
| Golden Carrot | 6 | 14.4 | Craft: 8 gold nuggets + carrot |
| Steak | 8 | 12.8 | Cook beef from cows |
| Pork Chop | 8 | 12.8 | Cook porkchop from pigs |
| Cooked Salmon | 6 | 9.6 | Cook fish from fishing/ocean |
| Bread | 5 | 6.0 | Craft: 3 wheat |
| Cooked Chicken | 6 | 7.2 | Cook chicken from chickens |
| Baked Potato | 5 | 6.0 | Cook potato in furnace |

**Emergency Foods** (Low Quality):
| Food | Hunger | Saturation | Notes |
|------|--------|------------|-------|
| Cookie | 2 | 0.4 | Wheat + cocoa beans |
| Melon Slice | 2 | 1.2 | Found in jungle, farmable |
| Apple | 4 | 2.4 | Tree drops (oak/dark oak) |
| Raw Meat | 3-4 | 1.8 | Risk of food poisoning |
| Rotten Flesh | 4 | 0.8 | 80% hunger effect chance |

### Food Acquisition Methods

**Hunting Animals**:
1. Find passive mobs (cows, pigs, chickens)
2. Kill with sword or tool (1-3 hits depending on tool)
3. Collect raw meat drops
4. Smelt in furnace with fuel
5. Cooked meat restores more hunger + no food poisoning

**Farming Crops**:
1. Craft hoe from sticks and material
2. Till dirt blocks near water (within 4 blocks)
3. Plant seeds (wheat from grass, or crop item)
4. Wait for growth (0-60 minutes depending on conditions)
5. Harvest when fully grown (yellow/brown appearance)
6. Replant from seeds

**Fishing**:
1. Craft fishing rod (3 sticks + 2 string)
2. Find water body (any depth, any size)
3. Cast line (right-click)
4. Wait for bobber to submerge
5. Reel in (right-click when bobber dips)
6. Collect fish or treasure

**Breeding Animals**:
1. Fence in two or more same-species animals
2. Feed each the appropriate food (wheat for cows/sheep)
3. Hearts appear, animals enter "love mode"
4. Baby animal spawns
5. Baby grows in 20 minutes (can speed with food)
6. Sustainable food source

### Crop Farming Details

**Wheat**:
- **Seeds From**: Breaking tall grass
- **Growth**: 8 stages, ~60 minutes
- **Uses**: Bread, breeding cows/sheep/horses
- **Harvest**: Wheat + 1-3 seeds

**Carrots/Potatoes**:
- **Seeds From**: Zombie drops, village farms
- **Growth**: 8 stages, ~60 minutes
- **Uses**: Direct food (potatoes must be cooked)
- **Harvest**: 1-4 carrots/potatoes

**Beetroot**:
- **Seeds From**: Village farms, dungeon chests
- **Growth**: 4 stages, ~60 minutes
- **Uses**: Beetroot soup, red dye
- **Harvest**: Beetroot + 0-3 seeds

**Farming Optimization**:
- **Water**: Must be within 4 blocks of farmland
- **Light**: Level 9+ required for growth
- **Bone Meal**: Instantly advances growth stages
- **Trampling**: Jumping on farmland destroys it

## Combat System

### Damage Types

**Melee Damage** (Close Range):
- **Bare Hands**: 1 damage (very slow)
- **Wooden Sword**: 4 damage
- **Stone Sword**: 5 damage
- **Iron Sword**: 6 damage
- **Diamond Sword**: 7 damage
- **Netherite Sword**: 8 damage

**Attack Cooldown**:
- Each attack requires cooldown before full damage
- Indicator appears below crosshair
- Attacking before cooldown = reduced damage (~50%)
- Swords have fastest cooldown (0.625s)

**Ranged Damage** (Distance):
- **Bow**: 1-10 damage (charge dependent)
- **Fully Charged**: Maximum damage + critical hit (1.5x)
- **Arrow Types**: Normal, poison, harming, fire
- **Range**: Effective up to 50 blocks

### Combat Strategies

**Hit-and-Run**:
1. Approach mob
2. Strike when attack cooldown complete
3. Back away immediately
4. Wait for cooldown while moving
5. Repeat until mob defeated
**Best For**: Single zombies, skeletons

**High Ground Advantage**:
1. Build 2-3 block pillar
2. Strike mobs from above
3. Mobs cannot reach player
4. Safe but slow method
**Best For**: Spider groups, mixed mobs

**Blocking with Shield**:
1. Craft shield (iron ingot + 6 planks)
2. Equip in off-hand
3. Hold right-click to block
4. Blocks 100% melee damage and arrows
5. Brief cooldown if hit by axe
**Best For**: Skeleton arrows, creepers

**Bow Combat**:
1. Craft bow (3 sticks + 3 string)
2. Craft arrows (flint + stick + feather)
3. Hold right-click to charge
4. Release to fire
5. Aim slightly above target for distance
**Best For**: Skeletons, creepers, kiting dangerous mobs

**Water Bucket Defense**:
1. Keep water bucket in hotbar
2. Place water at feet when overwhelmed
3. Mobs slow dramatically in water
4. Endermen teleport away from water
5. Pick up water when safe
**Best For**: Emergency escapes, creepers, endermen

### Armor System

**Armor Points**:
- **Full Bar**: 20 armor points (10 icons)
- **Each Point**: Reduces damage by 4%
- **Maximum Reduction**: 80% damage reduction (20 points)

**Armor Durability**:
- **Takes Damage**: When player is hit
- **Breaks**: Disappears when durability reaches 0
- **Repair**: Anvil + material or combine two damaged pieces

**Armor Set Comparison**:
| Material | Total Protection | Durability |
|----------|------------------|------------|
| Leather | 7 points (28%) | 80 total |
| Gold | 11 points (44%) | 112 total |
| Chainmail | 12 points (48%) | 240 total |
| Iron | 15 points (60%) | 240 total |
| Diamond | 20 points (80%) | 528 total |
| Netherite | 20 points (80%) | 592 total |

**Armor Priority**:
1. **Chestplate**: Highest protection per piece
2. **Leggings**: Second highest protection
3. **Helmet**: Third priority
4. **Boots**: Lowest protection but prevents some fall damage

### Defensive Structures

**Basic Wall**:
- **Height**: Minimum 2 blocks (prevents zombies)
- **Material**: Any solid block (cobblestone recommended)
- **Lighting**: Place torches on top to prevent mob spawning

**Moat Defense**:
- **Depth**: 2-3 blocks deep
- **Width**: 2+ blocks wide
- **Fill**: Water (slows mobs) or lava (kills mobs)
- **Note**: Spiders can still climb walls

**Safe Room Design**:
```
[Wall][Wall][Wall][Wall][Wall]
[Wall][Torch][ ][Torch][Wall]
[Wall][ ][Bed][ ][Wall]
[Wall][Chest][Table][Chest][Wall]
[Wall][Wall][Door][Wall][Wall]
```
- **Size**: 5×5 minimum
- **Lighting**: Multiple torches to prevent spawning
- **Essentials**: Bed, crafting table, chests
- **Door**: Wooden door (or iron with button)

## Mining and Ore Collection

### Mining Safety Rules

**Never Dig Straight Down**:
- Risk: Fall into lava, cave, or void
- Solution: Dig in 2×1 pattern (alternate blocks)

**Never Dig Straight Up**:
- Risk: Lava or gravel falls on you
- Solution: Stand to side while mining up

**Always Carry**:
1. **Pickaxe**: Primary tool + backup
2. **Torches**: Light source + mob prevention (stack of 64+)
3. **Food**: Cooked meat or bread (16+)
4. **Sword**: Combat defense
5. **Blocks**: Cobblestone for building (stack of 64)
6. **Water Bucket**: Lava emergencies

**Mark Your Path**:
- Place torches on right wall when entering
- Follow left wall torches to exit
- Prevents getting lost in cave systems

### Mining Techniques

**Surface Mining**:
- **Method**: Explore surface for exposed ores
- **Best For**: Early game coal and iron
- **Pros**: Safe, no digging required
- **Cons**: Limited ore quantity

**Cave Exploration**:
- **Method**: Explore natural cave systems
- **Best For**: All ores, fast collection
- **Pros**: High ore density, pre-cleared space
- **Cons**: Dangerous, many mobs, easy to get lost

**Strip Mining**:
- **Method**: Long straight tunnel at optimal Y-level
- **Tunnels**: 2 blocks high, 1 block wide
- **Spacing**: Every 3 blocks (leaves 2 blocks between)
- **Best For**: Diamond, gold, redstone
- **Pros**: Systematic, safe, thorough
- **Cons**: Time-consuming, repetitive

**Branch Mining**:
- **Method**: Main tunnel with side branches
- **Main Tunnel**: 2 high × 2 wide
- **Branches**: 2 high × 1 wide, every 3 blocks
- **Length**: 20-50 blocks per branch
- **Best For**: Diamond mining at Y=-59
- **Pros**: Very efficient, organized
- **Cons**: Requires planning, lots of torches

**Quarry Mining**:
- **Method**: Dig out entire area layer by layer
- **Size**: Variable (16×16 common)
- **Best For**: Clearing area for building
- **Pros**: Total resource collection, creates space
- **Cons**: Extremely time-consuming

### Ore Distribution by Y-Level

**Coal** (Most Common):
- **Y-Range**: 0 to 192
- **Peak**: Y 96, Y 136
- **Abundance**: Very common at all levels
- **Uses**: Fuel, torches
- **Tool Required**: Wooden pickaxe+

**Iron** (Essential Mid-Game):
- **Y-Range**: -64 to 320
- **Peak**: Y 16, Y 232
- **Abundance**: Common
- **Uses**: Tools, armor, buckets, rails
- **Tool Required**: Stone pickaxe+

**Copper** (Decorative):
- **Y-Range**: -16 to 112
- **Peak**: Y 48
- **Abundance**: Common
- **Uses**: Lightning rods, spyglass, building
- **Tool Required**: Stone pickaxe+

**Lapis Lazuli** (Enchanting):
- **Y-Range**: -64 to 64
- **Peak**: Y 0
- **Abundance**: Uncommon
- **Uses**: Enchanting, blue dye
- **Tool Required**: Stone pickaxe+

**Gold** (Utility):
- **Y-Range**: -64 to 32
- **Peak**: Y -16
- **Abundance**: Uncommon
- **Uses**: Powered rails, golden apples
- **Tool Required**: Iron pickaxe+

**Redstone** (Mechanisms):
- **Y-Range**: -64 to 16
- **Peak**: Y -59
- **Abundance**: Common below Y 0
- **Uses**: Circuits, mechanisms, brewing
- **Tool Required**: Iron pickaxe+

**Diamond** (Critical Late-Game):
- **Y-Range**: -64 to 16
- **Peak**: Y -59 (deepslate level)
- **Abundance**: Rare (1 ore per chunk average)
- **Uses**: Best tools/armor, enchanting table
- **Tool Required**: Iron pickaxe+

**Emerald** (Trading):
- **Y-Range**: -16 to 320
- **Peak**: Y 224 (mountain biomes only)
- **Abundance**: Very rare
- **Uses**: Trading with villagers
- **Tool Required**: Iron pickaxe+

### Optimal Mining Strategies by Goal

**Early Game (First Day)**:
- **Goal**: Get iron quickly
- **Method**: Surface/cave mining at Y 0-60
- **Target**: 10-20 iron ore, coal

**Mid Game (Diamond Search)**:
- **Goal**: Find diamonds
- **Method**: Branch mining at Y -59
- **Duration**: 1-3 hours of mining
- **Target**: 3-6 diamonds minimum

**Late Game (Resource Farming)**:
- **Goal**: Mass resources
- **Method**: Strip mining or quarry
- **Duration**: Ongoing activity
- **Target**: Full chests of materials

### Cave Exploration Tips

**Lighting Protocol**:
1. Place torches every 8-10 blocks
2. Light all intersections completely
3. Block off unexplored tunnels with cobblestone
4. Mark explored areas distinctly

**Lava Safety**:
- **Indicator**: Orange glow, bubbling sound
- **Never**: Jump over lava gaps
- **Always**: Bridge with blocks
- **Emergency**: Water bucket extinguishes fire

**Water Hazards**:
- **Drowning**: 20 seconds of breath
- **Solution**: Swim up or place blocks to air pocket
- **Use**: Water breaks fall damage

**Mob Spawner Rooms**:
- **Identification**: Cage block with spinning mob inside
- **Danger**: Continuous mob spawning in darkness
- **Solution**: Place torches on top of spawner
- **Value**: Can be converted to XP farm

## Building and Shelter

### First Night Shelter

**Emergency Shelter (5 minutes)**:
1. Dig 3 blocks into hill or ground
2. Place door in entrance
3. Place crafting table inside
4. Place torch for light
5. Seal entrance if no door

**Basic House (Day 1-2)**:
```
Size: 7×7 exterior (5×5 interior)
Height: 3 blocks tall interior
Walls: Cobblestone or wood planks
Roof: Any solid blocks
Door: Wooden door
Lighting: 4-6 torches inside
Furniture: Bed, crafting table, 2-3 chests, furnace
```

**Construction Steps**:
1. Clear flat 7×7 area
2. Place floor blocks (optional but recommended)
3. Build walls 4 blocks high on perimeter
4. Leave 1-block gap for door
5. Place roof covering entire top
6. Install door
7. Place torches on walls inside
8. Arrange furniture against walls

### Advanced Building Concepts

**Room Dimensions**:
- **Small Room**: 5×5 (interior)
- **Medium Room**: 7×7 to 9×9
- **Large Room**: 11×11+
- **Ceiling Height**: 3 blocks minimum (comfortable)

**Multi-Floor Buildings**:
- **Stairs**: 1 block step + 1 block rise
- **Ladders**: Vertical climbing, 2 blocks wide for safety
- **Floor Thickness**: 1 block minimum (use solid blocks)

**Material Choices**:

**Structural (Load-Bearing)**:
- **Stone/Cobblestone**: Durable, blast-resistant, non-flammable
- **Stone Bricks**: Decorative, same durability as stone
- **Wood Planks**: Flammable, various colors, renewable

**Decorative (Non-Structural)**:
- **Glass**: Windows, transparent
- **Wool**: Soft appearance, flammable, many colors
- **Concrete**: Vibrant colors, requires water + powder crafting
- **Stairs/Slabs**: Half-blocks for detail and depth

**Functional Blocks**:
- **Doors**: Wooden (manual), iron (redstone)
- **Trapdoors**: Horizontal doors, decorative
- **Fences**: 1.5 blocks high, mobs can't jump
- **Gates**: Fence doors
- **Buttons/Levers**: Redstone controls

### Base Layout Design

**Starter Base Components**:
```
[Storage Room]──[Crafting Area]──[Smelting Room]
      │              │                  │
[Bedroom]────[Central Hall]────[Entrance Airlock]
      │              │                  │
[Farm Area]──[Utility Room]────[Animal Pens]
```

**Room Purposes**:

**Storage Room**:
- Multiple chests organized by category
- Item frames for labeling
- Barrels for additional storage

**Crafting Area**:
- Crafting table (center access)
- Clear 3×3 floor space
- Nearby storage for materials

**Smelting Room**:
- 4-8 furnaces in row
- Chest for fuel input
- Chest for raw materials
- Chest for finished products

**Bedroom**:
- Bed (respawn point)
- Personal chest for valuables
- Armor stand for extra armor

**Entrance Airlock**:
- Double-door system
- Prevents mobs entering when opening door
- Well-lit interior and exterior

**Farm Area**:
- Water channels (4 blocks between)
- Torch lighting or skylights
- Chest for seeds and harvests

### Lighting Strategies

**Interior Lighting**:
- **Torch Spacing**: Every 6-7 blocks
- **Light Level**: Must reach 8+ everywhere
- **Placement**: Walls, floor (on blocks), ceiling (glowstone/lanterns)
- **Aesthetic**: Hidden lighting (under carpets, behind stairs)

**Exterior Lighting**:
- **Perimeter**: Torches every 8 blocks in square around base
- **Pathways**: Light both sides of paths
- **Height**: Place on fence posts for visibility
- **Purpose**: Prevent mob spawning within 128-block radius

**Light Sources Comparison**:
| Source | Light Level | Fuel/Crafting |
|--------|-------------|---------------|
| Torch | 14 | Coal + stick |
| Lantern | 15 | Iron + torch |
| Glowstone | 15 | Nether material |
| Sea Lantern | 15 | Ocean monument |
| Jack o'Lantern | 15 | Pumpkin + torch |
| Redstone Lamp | 15 | Redstone + glowstone |

### Defensive Architecture

**Wall Construction**:
- **Height**: 3+ blocks (prevents spiders)
- **Thickness**: 1 block (2 for blast resistance)
- **Material**: Cobblestone (explosion resistant)
- **Top**: Place lighting or half-slabs

**Moat Systems**:
- **Width**: 3+ blocks (zombies can't cross)
- **Depth**: 3+ blocks
- **Fill Options**:
  - Empty: Mobs fall in, trapped
  - Water: Slows mobs significantly
  - Lava: Kills mobs, destroys drops
  - Cactus: Damages mobs over time

**Gate Systems**:
- **Piston Doors**: Hidden, secure, complex
- **Iron Doors**: Require button/lever/pressure plate
- **Fence Gates**: Simple, can be opened quickly

**Watchtowers**:
- **Height**: 10-15 blocks
- **Top Platform**: 3×3 or 5×5
- **Access**: Internal ladder
- **Function**: Scan horizon, bow combat position

## Enchanting and Experience

### Experience (XP) System

**Gaining XP**:
- **Mining Ores**: Coal, diamond, redstone, lapis, emerald
- **Killing Mobs**: 5 XP for most hostiles, 12 for baby animals
- **Breeding**: 1-7 XP per baby animal born
- **Fishing**: 1-6 XP per catch
- **Smelting**: Varies by item (0.1 to 1 XP each)
- **Trading**: 3-6 XP per villager trade

**XP Levels**:
- **Level 1-16**: 17 XP per level (linear)
- **Level 17-31**: Increases by 3 per level
- **Level 32+**: Increases by 7 per level
- **Display**: Green bar below hotbar

**XP Usage**:
- **Enchanting**: 1-3 levels per enchant
- **Anvil Repairs**: Variable cost (increases with use)
- **Anvil Combining**: Enchanted items merge

### Enchanting Table Setup

**Crafting Enchanting Table**:
```
Recipe:
[ ][Book][ ]
[Diamond][Obsidian][Diamond]
[Obsidian][Obsidian][Obsidian]

Requirements:
- 4 obsidian blocks (mine with diamond pickaxe)
- 2 diamonds
- 1 book (3 paper + 1 leather)
```

**Bookshelf Enhancement**:
- **Maximum**: 15 bookshelves
- **Placement**: 1 block away from table, 2 blocks high
- **Pattern**: Surrounding rectangle with 1-block gap
- **Effect**: Unlocks level 30 enchantments (maximum power)

**Optimal Layout**:
```
[BS][BS][BS][BS][BS]
[BS][ ][ ][ ][BS]
[BS][ ][ET][ ][BS]
[BS][ ][ ][ ][BS]
[BS][BS][BS][BS][BS]

BS = Bookshelf
ET = Enchanting Table
[ ] = Air gap (required)
```

### Common Enchantments

**Tool Enchantments**:
- **Efficiency** (I-V): Faster mining speed
- **Fortune** (I-III): More drops from ores (diamonds!)
- **Silk Touch** (I): Blocks drop themselves (grass, ice, ore blocks)
- **Unbreaking** (I-III): Increased durability
- **Mending**: Repair with XP orbs (extremely valuable)

**Weapon Enchantments**:
- **Sharpness** (I-V): Increased damage to all mobs
- **Smite** (I-V): Increased damage to undead (zombies, skeletons)
- **Bane of Arthropods** (I-V): Increased damage to spiders
- **Knockback** (I-II): Pushes mobs back when hit
- **Fire Aspect** (I-II): Sets mobs on fire
- **Looting** (I-III): Increased mob drops (very useful)

**Armor Enchantments**:
- **Protection** (I-IV): General damage reduction
- **Fire Protection** (I-IV): Reduces fire/lava damage
- **Blast Protection** (I-IV): Reduces explosion damage
- **Projectile Protection** (I-IV): Reduces arrow damage
- **Thorns** (I-III): Reflects damage to attacker
- **Feather Falling** (I-IV): Reduces fall damage (boots only)

**Bow Enchantments**:
- **Power** (I-V): Increased arrow damage
- **Punch** (I-II): Increased knockback
- **Flame** (I): Arrows set targets on fire
- **Infinity** (I): Never consume arrows (need 1 arrow)

**Priority Enchantments**:
1. **Diamond Pickaxe**: Efficiency V, Fortune III, Unbreaking III
2. **Diamond Sword**: Sharpness V, Looting III, Unbreaking III
3. **Diamond Armor**: Protection IV, Unbreaking III
4. **Bow**: Power V, Infinity, Unbreaking III

### Enchanting Strategy

**Lapis Lazuli Requirement**:
- 1-3 lapis lazuli per enchant
- Placed in left slot of enchanting table
- Mine at Y=0 for best lapis rates

**Enchantment Selection**:
1. Place item in enchanting table
2. Place 1-3 lapis lazuli in slot
3. See 3 enchantment options (cost 1, 2, or 3 levels)
4. Higher cost = better enchantments
5. Select desired enchantment
6. Item is enchanted and removed

**Optimizing Enchantments**:
- **Level 30**: Best enchantments, multiple per item
- **Books**: Enchant books, combine at anvil later
- **Grindstone**: Remove unwanted enchantments, recover XP
- **Anvil**: Combine books or items, repair items

## Redstone Basics

### Redstone Components

**Power Sources**:
- **Redstone Torch**: Always on, inverted by block input
- **Lever**: Toggle on/off manually
- **Button**: Temporary power (1.5 seconds)
- **Pressure Plate**: Activates when stepped on
- **Daylight Sensor**: Power based on sunlight

**Transmission**:
- **Redstone Dust**: Transmits power up to 15 blocks
- **Redstone Repeater**: Extends signal, adds delay
- **Redstone Comparator**: Compares signal strengths

**Output Devices**:
- **Piston**: Pushes blocks 1 space
- **Sticky Piston**: Pushes and pulls blocks
- **Dispenser**: Shoots items/projectiles
- **Dropper**: Drops items
- **Redstone Lamp**: Light source (on/off)
- **Door/Trapdoor**: Opens when powered
- **TNT**: Explodes when powered

### Simple Redstone Contraptions

**Automatic Door**:
```
[Pressure Plate]
[Block with Iron Door]
[Block]
[Redstone Dust to door]
```
Steps on plate → Door opens → Steps off → Door closes

**Hidden Entrance (Piston Door)**:
```
[Lever]→[Redstone]→[Sticky Piston]→[Block]
```
Flip lever → Piston extends → Block moves → Entrance revealed

**Item Sorter**:
Uses hoppers + comparators to sort items into different chests
(Complex - requires tutorial for full setup)

**Mob Farm**:
Dark spawning room → Water channels → Central collection → Kill chamber
(Generates drops automatically)

### Redstone Power Rules

**Power Levels**:
- **15**: Maximum (source blocks)
- **14-1**: Decreases by 1 per block of redstone dust
- **0**: No power (off state)

**Repeater Function**:
- Resets power to 15
- Adds 1-4 tick delay (adjustable)
- Only transmits one direction
- Essential for long-distance circuits

**Piston Mechanics**:
- **Can Push**: Most solid blocks (max 12 blocks)
- **Cannot Push**: Obsidian, bedrock, furnaces, chests
- **Sticky Piston**: Pulls blocks back when deactivated
- **Uses**: Hidden doors, bridges, farms, traps

## Villagers and Trading

### Finding Villagers

**Villages**:
- **Biomes**: Plains, desert, savanna, taiga, snowy tundra
- **Structure**: Houses, farms, wells, job sites
- **Population**: 10-20 villagers typically
- **Detection**: Bell sounds, doors, job site blocks

**Curing Zombie Villagers**:
1. Find zombie villager (5% of zombies)
2. Trap in enclosed space
3. Throw splash potion of weakness (brewing required)
4. Feed golden apple (8 gold ingots + apple)
5. Wait 3-5 minutes for conversion
6. Results in discounted trades

### Villager Professions

Profession determined by job site block:

| Profession | Job Site | Useful Trades |
|------------|----------|---------------|
| Armorer | Blast Furnace | Iron/diamond armor, chainmail |
| Butcher | Smoker | Cooked meat, emeralds for raw meat |
| Cartographer | Cartography Table | Maps, ocean explorer maps |
| Cleric | Brewing Stand | Redstone, glowstone, ender pearls |
| Farmer | Composter | Bread, golden carrots, emeralds for crops |
| Fisherman | Barrel | Fish, campfires, emeralds for fish |
| Fletcher | Fletching Table | Bows, arrows, crossbows |
| Leatherworker | Cauldron | Leather armor, saddles |
| Librarian | Lectern | Enchanted books, bookshelves, glass |
| Mason | Stonecutter | Bricks, terracotta, quartz |
| Shepherd | Loom | Wool, beds, paintings |
| Toolsmith | Smithing Table | Iron/diamond tools, bells |
| Weaponsmith | Grindstone | Iron/diamond swords, axes, emeralds |

### Trading Mechanics

**Emeralds**:
- Primary currency for all trades
- Obtained from mining (mountains) or trading
- Essential for villager economy

**Trade Levels**:
1. **Novice**: Basic trades, easy materials
2. **Apprentice**: Intermediate trades
3. **Journeyman**: Better trades
4. **Expert**: Advanced trades
5. **Master**: Best trades, rare items

**Leveling Up**:
- Trade with villager multiple times
- Each successful trade gives XP to villager
- Levels unlock better trades
- Can take 20-50 trades to reach Master

**Best Trades**:
- **Librarian**: Mending books, good enchantments
- **Armorer**: Diamond armor for emeralds
- **Toolsmith/Weaponsmith**: Diamond tools/weapons
- **Cleric**: Ender pearls (for End portal)
- **Farmer**: Emeralds for crops (easy profit)

**Trade Restocking**:
- Villagers restock trades twice per day
- Requires access to job site block
- Limited trades per restock
- Plan trading sessions around this

### Villager Breeding

**Requirements**:
1. **Beds**: 1 per villager + 1 for baby
2. **Food**: Bread (3), carrots/potatoes (12), or beetroot (12)
3. **Willingness**: Fed villagers enter "willing" mode
4. **Housing**: Enclosed space with beds

**Process**:
1. Build room with 3+ beds
2. Bring 2 villagers to room
3. Throw bread at them (they pick up)
4. Hearts appear, baby villager spawns
5. Baby grows in 20 minutes
6. Assign profession with job site block

**Population Expansion**:
- Each baby needs own bed to grow
- Add job sites for professions
- Create trading hall for organization
- Protect from zombies (lighting, walls)

## The Nether Dimension

### Nether Portal Construction

**Obsidian Frame**:
```
[Obs][Obs][Obs][Obs]
[Obs][ ][ ][Obs]
[Obs][ ][ ][Obs]
[Obs][ ][ ][Obs]
[Obs][Obs][Obs][Obs]

Size: 4×5 obsidian frame (corners optional)
```

**Building Portal**:
1. Obtain diamond pickaxe (only tool that mines obsidian)
2. Find lava lake
3. Pour water on lava to create obsidian
4. Mine obsidian (takes 9.4 seconds per block with diamond pickaxe)
5. Build 4-block wide, 5-block tall frame
6. Ignite portal with flint and steel
7. Purple swirling portal activates

**Flint and Steel**:
```
Recipe:
[Iron Ingot][ ]
[ ][Flint]
```
Used to ignite portal and start fires

### Nether Environment

**Appearance**:
- Red and brown terrain (netherrack, soul sand)
- Lava seas and lakes everywhere
- Floating islands, massive caverns
- No day/night cycle
- Hostile and dangerous

**Nether Blocks**:
- **Netherrack**: Red stone, catches fire permanently
- **Soul Sand**: Slows movement, creates bubble columns in water
- **Soul Soil**: Similar to soul sand, doesn't slow
- **Glowstone**: Bright light source blocks (ceiling)
- **Nether Quartz Ore**: White ore, used for redstone
- **Ancient Debris**: Extremely rare, used for netherite

**Environmental Hazards**:
- **Lava**: Everywhere, often hidden above
- **Fire**: Netherrack burns infinitely
- **Ghasts**: Explosive fireball attacks
- **Fall Damage**: Massive open spaces
- **Getting Lost**: Confusing layout, similar-looking terrain

### Nether Mobs

**Zombie Piglin**:
- **Health**: 20 HP
- **Damage**: 5-13 (difficulty dependent)
- **Behavior**: Neutral until attacked
- **Special**: Entire group aggros if one is hit
- **Drops**: Gold nuggets, gold swords
- **Strategy**: Avoid combat unless necessary

**Ghast**:
- **Health**: 10 HP
- **Damage**: 17 (fireball explosion)
- **Behavior**: Flies, shoots fireballs from distance
- **Special**: Fireballs can be deflected back
- **Drops**: Ghast tears (brewing), gunpowder
- **Strategy**: Use bow, deflect fireballs with sword timing

**Blaze**:
- **Health**: 20 HP
- **Damage**: 5-9 per fireball
- **Location**: Nether fortresses only
- **Special**: Flies, shoots 3 fireballs
- **Drops**: Blaze rods (brewing, Eye of Ender)
- **Strategy**: Snowballs (3 damage each), shield blocking

**Magma Cube**:
- **Health**: 4-16 HP (size dependent)
- **Damage**: 2-12 (size dependent)
- **Behavior**: Bounces, splits when killed
- **Special**: Immune to fire and lava
- **Drops**: Magma cream
- **Strategy**: Fight from distance or elevated position

**Wither Skeleton**:
- **Health**: 20 HP
- **Damage**: 8 + Wither II effect (poisoning)
- **Location**: Nether fortresses
- **Special**: Inflicts wither effect (health drain)
- **Drops**: Coal, bones, rarely wither skeleton skull
- **Strategy**: Keep distance, bring milk to cure wither

### Nether Resources

**Blaze Rods**:
- **Source**: Killing blazes in fortresses
- **Uses**: Brewing stand, Eyes of Ender (End portal)
- **Importance**: Required for game progression
- **Collection**: Kill 10+ blazes minimum

**Nether Wart**:
- **Source**: Nether fortress stairwells
- **Uses**: Primary brewing ingredient
- **Growing**: Place on soul sand in any dimension
- **Importance**: Essential for all potions

**Glowstone**:
- **Source**: Ceiling clusters in Nether
- **Uses**: Bright lighting (level 15), redstone
- **Collection**: Breaks into 2-4 dust, craft back to block
- **Tool**: Any tool or hand

**Netherite (End-Game)**:
- **Source**: Ancient debris (Y 8-22, very rare)
- **Processing**: Smelt debris → netherite scrap → 4 scraps + 4 gold = netherite ingot
- **Uses**: Upgrade diamond gear at smithing table
- **Properties**: Fire-proof, highest durability, doesn't burn in lava

### Nether Survival Tips

**Preparation Checklist**:
- Full iron or diamond armor
- Diamond sword and bow
- 64+ arrows
- 64+ building blocks (cobblestone)
- Food (32+ cooked meat)
- Flint and steel (backup portal ignition)
- Fire resistance potions (if available)

**Nether Strategy**:
1. Build protective structure around portal (cobblestone box)
2. Mark portal coordinates in Overworld notes
3. Light area around portal thoroughly
4. Bridge carefully over lava (crouch to not fall)
5. Build safe paths with railings
6. Mark path back to portal with distinct blocks
7. Never mine straight up or down

**Finding Nether Fortress**:
- Look for dark brick structures
- Often along Z-axis (North-South corridors)
- Travel far from portal (300+ blocks common)
- Build bridges across lava seas
- Mark route with torches and cobblestone pillars

**Emergency Procedures**:
- **Portal Destroyed**: Rebuild frame, ignite with flint & steel
- **No Flint & Steel**: Ghast fireball can ignite portal
- **Lost**: Build tall pillar, write down coordinates
- **Overwhelmed**: Build 1×1 pillar, heal, plan escape

## The End Dimension

### Locating Stronghold

**Eyes of Ender**:
```
Recipe: 1 Ender Pearl + 1 Blaze Powder
Source: Ender pearls from endermen, blaze powder from blaze rods
```

**Finding Stronghold**:
1. Craft 12+ Eyes of Ender
2. Right-click to throw Eye in the air
3. Eye floats toward nearest stronghold
4. Follow direction Eye travels
5. Repeat every 20-30 blocks
6. Eye floats downward when above stronghold
7. Dig down to find structure (Y 20-40)
8. Eyes have 20% chance to break when used

**Stronghold Structure**:
- Stone brick corridors and rooms
- Library rooms (bookshelves, valuable)
- Portal room (End portal frame)
- Silverfish spawners (dangerous)

**Activating End Portal**:
1. Locate portal room (12-frame square over lava)
2. Place Eyes of Ender in each frame slot (need 12 total)
3. All frames must have eyes to activate
4. Portal opens with black starry appearance
5. Jump in to enter The End

### The End Environment

**Appearance**:
- Floating islands in void
- Pale yellow endstone terrain
- Black sky with stars
- Main island with obsidian pillars
- No sun, moon, or weather

**Immediate Dangers**:
- **Void**: Fall off edge = instant death, lose all items
- **Endermen**: Everywhere, very dangerous in groups
- **Ender Dragon**: Attacks immediately
- **No Bed**: Beds explode in The End

**Obsidian Pillars**:
- 10 pillars of varying heights
- Each has End Crystal on top
- Crystals heal the Ender Dragon
- Must be destroyed before fighting dragon

### Ender Dragon Fight

**Preparation**:
- Full diamond or netherite armor (Protection IV ideal)
- Diamond sword (Sharpness V)
- Bow with 128+ arrows (Power V, Infinity)
- 64+ building blocks (cobblestone/endstone)
- Food (golden carrots or steak, 32+)
- Water bucket (for safe descent)
- Slow falling or feather falling (optional but helpful)

**Phase 1: Destroy End Crystals**:
1. Shoot crystals with bow (they explode)
2. Some crystals have cages (must climb and break)
3. Build pillars with blocks to reach high crystals
4. Water bucket for safe descent from pillars
5. Destroy all 10 crystals before dragon fight

**Phase 2: Dragon Combat**:
- **Dragon's Attacks**:
  - Dive bomb: Rams player for heavy damage
  - Dragon breath: Purple acid cloud, lingering damage
  - Ender acid fireballs: Spawns damaging clouds
  
- **Attack Timing**:
  - Wait for dragon to perch on portal (center)
  - Rush in and attack head with sword
  - 8-10 hits before dragon flies away
  - Shoot with bow while dragon flying
  - Avoid dragon breath clouds

- **Enderman Management**:
  - Wear pumpkin on head (prevents aggro when looking)
  - Or: Don't look at endermen, avoid eye contact
  - Build 2-block high shelter if overwhelmed

**Victory**:
- Dragon dies in explosion
- 12,000 XP orbs spawn (instant level 60+)
- Dragon egg appears on exit portal
- End gateway portals spawn (access outer islands)
- "Free the End" achievement

**Exit Portal**:
- Jump into bedrock fountain
- Credits roll (can skip)
- Return to Overworld spawn point
- Can return to End anytime through same portal

### End City and Outer Islands

**Accessing Outer Islands**:
1. Find end gateway portal (small bedrock frame)
2. Throw ender pearl through or bridge across
3. Outer islands are 1000+ blocks away
4. End cities spawn on outer islands

**End Cities**:
- Purple structures with towers
- Shulkers (mob that shoots levitation projectiles)
- Loot chests with diamond gear, enchanted items
- End ships sometimes attached (elytra location)

**Elytra (Wings)**:
- Found in End ships (hanging in item frame)
- Allows gliding when jumping from heights
- Must be equipped in chestplate slot
- Repaired with phantom membranes or anvil
- Most valuable item in game (flight capability)

**Shulker Boxes**:
- Crafted from shulker shells (2) + chest (1)
- Portable storage that keeps items when broken
- Essential for inventory management
- 27 slots like regular chest

## Potion Brewing

### Brewing Stand Setup

**Crafting Brewing Stand**:
```
Recipe:
[ ][Blaze Rod][ ]
[Cobble][Cobble][Cobble]

Requires: 1 Blaze Rod (from Nether blazes) + 3 Cobblestone
```

**Brewing Interface**:
- 3 bottom slots: Bottles for potions
- Top slot: Ingredient for brewing
- Left fuel slot: Blaze powder (powers brewing)

**Glass Bottles**:
```
Recipe: 3 glass in V-shape
Function: Right-click water source to fill
Essential: Need filled bottles to start brewing
```

### Potion Crafting Process

**Base Potion**:
```
Water Bottle + Nether Wart = Awkward Potion
(Awkward Potion is base for all effect potions)
```

**Common Effect Potions**:
| Ingredient | Effect | Duration | Usage |
|------------|--------|----------|-------|
| Magma Cream | Fire Resistance | 3:00 | Nether, lava protection |
| Sugar | Speed | 3:00 | Fast movement, escapes |
| Glistering Melon | Instant Health | Instant | Healing in combat |
| Golden Carrot | Night Vision | 3:00 | See in darkness/underwater |
| Pufferfish | Water Breathing | 3:00 | Ocean exploration |
| Spider Eye | Poison | 0:45 | Offensive (weak) |
| Blaze Powder | Strength | 3:00 | Increased melee damage |
| Ghast Tear | Regeneration | 0:45 | Health over time |
| Rabbit's Foot | Jump Boost | 3:00 | Jump higher |

**Modifying Potions**:
- **Redstone Dust**: Extends duration (8:00)
- **Glowstone Dust**: Increases effect level (II)
- **Gunpowder**: Converts to splash potion (throwable)
- **Dragon's Breath**: Converts to lingering potion (area effect)

**Example: Fire Resistance II**:
1. Fill 3 glass bottles with water
2. Add Nether Wart → Awkward Potion
3. Add Magma Cream → Fire Resistance (3:00)
4. Add Glowstone Dust → Fire Resistance II (1:30)

**Priority Potions**:
1. **Fire Resistance**: Essential for Nether
2. **Night Vision**: Mining and caves
3. **Water Breathing**: Ocean exploration
4. **Strength II**: Boss fights
5. **Healing II**: Emergency health

### Ingredient Sources

- **Nether Wart**: Nether fortress farms
- **Magma Cream**: Magma cubes or craft (blaze powder + slime ball)
- **Sugar**: Sugar cane farming
- **Glistering Melon**: Craft (melon slice + gold nuggets)
- **Golden Carrot**: Craft (carrot + gold nuggets)
- **Pufferfish**: Fishing
- **Blaze Powder**: Craft from blaze rods
- **Ghast Tear**: Ghast drops
- **Rabbit's Foot**: Rabbit drops (rare)

## Advanced Game Mechanics

### Hunger and Saturation Details

**Hidden Saturation System**:
- Each food has hidden saturation value
- Saturation depletes before visible hunger
- Better foods = longer before hunger decreases
- Why golden carrots are best (high saturation)

**Food Efficiency**:
| Food | Hunger | Saturation | Efficiency |
|------|--------|------------|------------|
| Golden Carrot | 6 | 14.4 | 2.4 |
| Suspicious Stew | 6 | 7.2 | 1.2 |
| Steak | 8 | 12.8 | 1.6 |
| Cooked Salmon | 6 | 9.6 | 1.6 |

**Efficiency** = Saturation / Hunger (higher = better)

**Food Poisoning**:
- **Raw Chicken**: 30% chance of 30-second hunger effect
- **Rotten Flesh**: 80% chance of 30-second hunger effect
- **Pufferfish**: Poison IV, nausea, hunger III (nearly fatal)
- **Spider Eye**: 4-second poison
- **Chorus Fruit**: Random teleportation

### Damage Types and Armor Effectiveness

**Damage Categories**:

**Physical Damage** (Reduced by armor):
- Mob melee attacks
- Player melee attacks
- Projectile damage (arrows, tridents)
- Falling anvils

**Environmental Damage** (Partially reduced by armor):
- Fall damage (40% reduction per protection level)
- Explosion damage (armor + enchantments)

**Magical Damage** (Not reduced by armor):
- Potion effects (poison, wither)
- Instant damage
- Hunger damage
- Void damage (instant death)

**Fire Damage** (Special case):
- Reduced by armor
- Negated by Fire Protection enchantment
- Negated by Fire Resistance potion

**Protection Enchantment Effectiveness**:
| Enchantment | Best For | Damage Reduction |
|-------------|----------|------------------|
| Protection IV | General use | 16% per piece (64% full set) |
| Fire Protection IV | Nether | 32% fire per piece |
| Blast Protection IV | Creepers | 32% explosion per piece |
| Projectile Protection IV | Skeletons | 32% projectile per piece |

### Status Effects

**Positive Effects**:
- **Regeneration**: 1 HP every 2.5 seconds
- **Speed**: 20% movement speed increase per level
- **Jump Boost**: Jump 0.5 blocks higher per level
- **Strength**: +3 damage per level
- **Fire Resistance**: Immunity to fire and lava
- **Water Breathing**: Prevents drowning
- **Night Vision**: See clearly in darkness
- **Invisibility**: Mobs can't see player (unless armor worn)
- **Absorption**: Temporary extra hearts

**Negative Effects**:
- **Poison**: Lose health over time (can't kill)
- **Wither**: Lose health over time (can kill)
- **Hunger**: Hunger depletes faster
- **Weakness**: Reduced melee damage
- **Slowness**: Reduced movement speed
- **Mining Fatigue**: Slower mining speed
- **Nausea**: Screen distortion
- **Blindness**: Limited vision range

**Curing Effects**:
- **Milk Bucket**: Removes all effects (good and bad)
- **Honey Bottle**: Removes poison effect
- **Wait**: Most effects expire over time

### Farming Automation

**Automatic Crop Farm**:
```
Components:
- Water channels (hydrate farmland)
- Observer blocks (detect crop growth)
- Pistons (break grown crops)
- Hopper system (collect items)
- Chest (storage)
```

**Redstone Clock Types**:
- **Repeater Clock**: Loops signal continuously
- **Hopper Clock**: Uses item transfer timing
- **Observer Clock**: Uses block updates
- **Daylight Sensor**: Activates at specific times

**Animal Breeding Automation**:
1. Automatic feeding system (dispenser)
2. Baby animal sorting (height-based gates)
3. Automatic collection (minecarts/hoppers)
4. Kill chamber with lava or suffocation
5. Item collection system

### Transportation Systems

**Minecart Rails**:
- **Rail**: Basic, no propulsion
- **Powered Rail**: Accelerates cart when powered
- **Detector Rail**: Outputs redstone signal
- **Activator Rail**: Activates TNT minecarts

**Minecart Design**:
```
Pattern for speed:
[Powered][Powered][Powered][Normal][Normal][Normal]
Repeat pattern with redstone torch every 34 blocks
```

**Horse Travel**:
- **Speed**: Varies by horse (7-14 m/s)
- **Jump**: Varies by horse (2-5 blocks)
- **Equipment**: Saddle (required), horse armor (protection)
- **Benefits**: Fast overland travel, no fuel

**Elytra Flight** (End-Game):
- **Launch**: Jump from height, press jump in air
- **Glide**: Glide at 10.9 m/s base speed
- **Rocket Boost**: Use firework rockets for acceleration
- **Durability**: 432 uses, repair with phantom membranes
- **Best Travel**: Fastest transportation method

**Nether Highway** (Efficient):
- **Distance Ratio**: 1 block Nether = 8 blocks Overworld
- **Travel**: Build tunnel in Nether (Y=120 for safety)
- **Speed**: Minecart or ice boat for fastest travel
- **Calculation**: 1000 blocks Overworld = 125 blocks Nether

### Beacon Setup

**Beacon Crafting**:
```
Recipe:
[Glass][Glass][Glass]
[Glass][Nether Star][Glass]
[Obsidian][Obsidian][Obsidian]

Nether Star from: Wither boss kill
```

**Pyramid Base**:
```
Level 1 (1 effect):
9 blocks (3×3 base)

Level 2 (1 effect + range):
34 blocks (5×5 base + 3×3 second layer)

Level 3 (2 effects):
83 blocks (7×7 + 5×5 + 3×3)

Level 4 (2 effects + range):
164 blocks (9×9 + 7×7 + 5×5 + 3×3)
```

**Beacon Materials** (Any single type):
- Iron blocks
- Gold blocks
- Diamond blocks
- Emerald blocks
- Netherite blocks

**Beacon Effects**:
- **Speed**: Movement speed increase
- **Haste**: Mining speed increase
- **Resistance**: Damage reduction
- **Jump Boost**: Higher jumping
- **Strength**: Melee damage increase
- **Regeneration**: Health regeneration (requires level 4)

**Effect Range**:
- Level 1: 20 block radius
- Level 2: 30 block radius
- Level 3: 40 block radius
- Level 4: 50 block radius

## AI Agent-Specific Strategies

### Decision-Making Framework

**Priority Assessment System**:
```
1. Survival (Health < 50%, Hunger < 10)
   → Eat food, retreat to safety, avoid combat

2. Critical Resources (No tools, no food, no shelter)
   → Gather wood, craft tools, find food

3. Safety (Night approaching, hostile mobs nearby)
   → Light area, build shelter, prepare defenses

4. Progression (Tier advancement, new areas)
   → Mine ores, craft better equipment, explore

5. Optimization (Storage, farms, automation)
   → Organize base, build farms, create systems
```

**State Evaluation Checklist**:
```python
# Pseudo-code for agent state assessment
if health < 10:
    PRIORITY = CRITICAL_DANGER
    ACTION = retreat_and_heal()
elif hunger < 6:
    PRIORITY = HIGH
    ACTION = find_and_eat_food()
elif is_night() and not in_shelter:
    PRIORITY = HIGH
    ACTION = return_to_base()
elif tool_durability < 25%:
    PRIORITY = MEDIUM
    ACTION = craft_replacement_tool()
elif inventory_full:
    PRIORITY = MEDIUM
    ACTION = return_and_store_items()
else:
    PRIORITY = LOW
    ACTION = continue_current_task()
```

### Pathfinding Considerations

**Obstacle Types**:

**Avoidable** (Navigate around):
- Water (slows movement unless boat)
- Lava (fatal unless fire resistance)
- Cacti (damage on contact)
- Sweet berry bushes (damage and slow)
- Campfires (damage unless crouching)

**Climbable** (Use alternative path):
- Walls 2+ blocks high (unless ladders)
- Cliffs and steep terrain
- Ravines (bridge required)

**Passable** (Direct traversal):
- Grass, flowers, dead bushes
- Open doors
- Gaps <4 blocks wide (jump)
- 1-block elevation changes

**Navigation Priorities**:
1. **Safety**: Avoid hazards over speed
2. **Efficiency**: Shortest safe path
3. **Resources**: Collect valuable materials en route
4. **Markers**: Note landmarks for return journey

### Resource Gathering Optimization

**Early Game Focus** (First 3 Days):
```
Priority Order:
1. Wood (40+ logs) → Tools, crafting, fuel
2. Food (20+ cooked meat) → Hunger management
3. Coal (32+) → Torches, smelting
4. Iron (20+ ore) → Tool upgrade
5. Wool (3 for bed) → Respawn point
```

**Mid Game Focus** (Days 4-20):
```
Priority Order:
1. Diamond (6+) → Best tools
2. Obsidian (14) → Nether portal
3. Enchanting setup → Power boost
4. Sustainable food farm → Long-term hunger
5. Organized storage → Inventory management
```

**Late Game Focus** (Day 20+):
```
Priority Order:
1. Blaze rods (10+) → End portal
2. Ender pearls (12+) → Find stronghold
3. Nether fortress materials → Brewing
4. End city loot → Elytra, shulker boxes
5. Netherite (optional) → Best gear
```

### Combat Decision Tree

```
ENCOUNTER MOB:
│
├─ IF health > 75% AND well-equipped
│  └─ ENGAGE in combat
│     ├─ Creeper → Shoot from distance OR hit-and-run
│     ├─ Skeleton → Use cover, rush with shield
│     ├─ Zombie → Melee, back away between hits
│     ├─ Spider → Fight in enclosed space
│     └─ Enderman → Avoid eye contact OR trap under 3-block ceiling
│
├─ IF health 50-75% OR moderate equipment
│  └─ ASSESS SITUATION
│     ├─ Single mob → Engage cautiously
│     ├─ Multiple mobs → Kite to separate
│     └─ Dangerous mob (creeper near base) → Prioritize elimination
│
└─ IF health < 50% OR poorly equipped
   └─ RETREAT
      ├─ Build 3-block pillar
      ├─ Enter water (slows mobs)
      ├─ Run to shelter
      └─ Heal before re-engaging
```

### Tool Management Protocol

**Durability Monitoring**:
```
Tool Durability States:
- 100-50%: GOOD (use normally)
- 49-25%: CAUTION (monitor closely)
- 24-10%: WARNING (craft replacement)
- 9-1%: CRITICAL (switch immediately)
- 0%: BROKEN (tool destroyed)
```

**Tool Switching Logic**:
```
if current_tool.durability < 25%:
    if backup_tool exists:
        switch_to(backup_tool)
        add_to_crafting_queue(current_tool.type)
    else:
        if can_craft_replacement():
            craft_new_tool()
        else:
            return_to_base("need materials for tool")
```

**Tool Prioritization**:
```
Critical (Always carry):
1. Pickaxe (+ backup)
2. Sword
3. Food (16+ units)

Important (Situational):
4. Axe (when chopping wood)
5. Shovel (when mining dirt/sand)
6. Torches (when mining/exploring)

Optional (Task-specific):
7. Hoe (when farming)
8. Bow + Arrows (when combat-focused)
9. Water bucket (when near lava)
10. Fishing rod (when near water)
```

### Mining Efficiency Algorithms

**Strip Mining Pattern**:
```
// Optimal diamond mining at Y=-59
START at Y=-59
CREATE main_tunnel (2 high × 2 wide × 50 long)
FOR every 3 blocks along main_tunnel:
    CREATE branch (2 high × 1 wide × 30 long)
    ALTERNATE sides (left, right, left, right)
    PLACE torch every 8 blocks
    MINE all visible ores
RETURN to main_tunnel entrance
STORE collected items
```

**Cave Exploration Protocol**:
```
ENTER cave system
PLACE torch on RIGHT wall (entrance marker)
WHILE exploring:
    CONTINUE placing torches on RIGHT wall
    BLOCK unexplored tunnels with cobblestone
    MARK dangerous areas (lava, spawners)
    COLLECT visible ores
TO EXIT:
    FOLLOW LEFT wall torches back to entrance
```

**Ore Priority in Caves**:
```
if sees_diamond:
    MINE immediately (highest priority)
elif sees_gold or sees_redstone:
    MINE after clearing area of mobs
elif sees_iron:
    MINE opportunistically
elif sees_coal:
    MINE if inventory space > 50%
else:
    IGNORE common blocks
```

### Inventory Management System

**Inventory Slot Assignment**:
```
Hotbar Layout:
Slot 1: Primary pickaxe
Slot 2: Sword
Slot 3: Food (cooked meat)
Slot 4: Torches
Slot 5: Building blocks (64 cobblestone)
Slot 6: Axe
Slot 7: Shovel  
Slot 8: Water bucket
Slot 9: Secondary tool/backup
```

**Inventory Cleanup Logic**:
```
if inventory_fullness > 75%:
    if near_base:
        RETURN and store items
    else:
        DROP low-value items (dirt, gravel, diorite)
        KEEP valuable items (ores, tools, food)
        
if inventory_fullness = 100%:
    STOP current task
    NAVIGATE to nearest chest
    STORE all non-essential items
```

**Item Value Classification**:
```
CRITICAL (Never drop):
- Tools (all types)
- Ores (diamond, iron, gold, redstone)
- Food (cooked meat, bread)
- Rare items (ender pearls, blaze rods)

VALUABLE (Keep if space):
- Building blocks (wood planks, stone)
- Coal
- Crafting materials (sticks, iron ingots)

COMMON (Drop if needed):
- Dirt, cobblestone (if have 64+)
- Gravel
- Granite, diorite, andesite
- Excess seeds
```

### Base Building Workflow

**Phase 1: Foundation** (Day 1)
```
1. SELECT flat 11×11 area near resources
2. CLEAR vegetation and hostile mobs
3. PLACE perimeter markers (torches)
4. BUILD 7×7 walls (cobblestone, 3 blocks high)
5. ADD roof (any solid blocks)
6. INSTALL door and interior lighting
7. PLACE bed, crafting table, chest
```

**Phase 2: Expansion** (Days 2-5)
```
1. ADD second room (storage)
   - Multiple chests by category
   - Item frames for labels
2. ADD third room (smelting)
   - 4-8 furnaces in row
   - Input/output chests
3. BUILD exterior wall (9×9 perimeter)
4. LIGHT entire perimeter (prevent spawns)
5. CREATE entrance airlock (double doors)
```

**Phase 3: Infrastructure** (Days 6-15)
```
1. BUILD farm area
   - Wheat, carrots, potatoes
   - Water channels, lighting
   - Chest for harvest storage
2. CREATE animal pens
   - Separate pens per species
   - Gates for access
   - Breeding area
3. ESTABLISH mineshaft entrance
   - Staircase or ladder shaft
   - Torch-lit descent
   - Storage at mining level
4. ADD watchtower (optional)
   - 10-15 blocks tall
   - 3×3 platform top
   - Bow combat position
```

### Time Management for AI

**Daytime Activities** (10 minutes):
```
OPTIMAL for:
- Surface exploration (no hostile mob spawns)
- Long-distance travel
- Building exterior structures
- Hunting animals for food
- Chopping trees in forest

AVOID:
- Underground mining (light doesn't matter)
- Interior crafting (inefficient use of safe time)
```

**Nighttime Activities** (7 minutes):
```
OPTIMAL for:
- Underground mining (always dark anyway)
- Crafting and smelting
- Organizing inventory and chests
- Enchanting items
- Breeding animals (if secure pen)

AVOID:
- Surface travel (hostile mob spawns)
- Outdoor building (combat interruptions)
- Hunting animals (mobs interfere)
```

**Time-Critical Decisions**:
```
if time = late_afternoon (3-4pm game time):
    if distance_to_base > 200 blocks:
        BEGIN return journey NOW
    elif critical_task_incomplete:
        WORK quickly to finish
        PREPARE for night defense
    else:
        RETURN to base early
        
if time = night AND outside_shelter:
    if near_base (< 50 blocks):
        SPRINT to base immediately
    else:
        DIG emergency shelter (3×3×2)
        PLACE door and torch
        WAIT for dawn (or sleep if have bed)
```

## Advanced AI Behavior Patterns

### Multi-Step Task Planning

**Example: "Get Diamonds"**:
```
GOAL: Obtain diamonds

CHECK prerequisites:
  [SUCCESS] Have iron pickaxe?
    NO → Gather iron ore → Smelt → Craft pickaxe
    YES → Continue
  [SUCCESS] Have food (20+)?
    NO → Hunt animals → Cook meat
    YES → Continue
  [SUCCESS] Have torches (64+)?
    NO → Gather coal → Craft torches
    YES → Continue

EXECUTE main task:
  1. Navigate to Y=-59 (best diamond level)
  2. BEGIN branch mining pattern
  3. MINE all diamond ore encountered
  4. MONITOR inventory space
  5. IF inventory full → Return to base
  6. CONTINUE until 3+ diamonds found

COMPLETE task:
  RETURN to base with diamonds
  STORE diamonds in valuable chest
  CRAFT diamond pickaxe
  MARK task as complete
```

**Complex Task: "Prepare for Nether"**:
```
GOAL: Ready for Nether expedition

PHASE 1 - Equipment:
  □ Full iron armor
  □ Iron sword (or better)
  □ Bow + 64 arrows
  □ Iron pickaxe (backup)
  □ 64 building blocks
  □ 32 food (cooked meat)

PHASE 2 - Portal:
  □ Mine 14 obsidian blocks (diamond pick required)
  □ Craft flint and steel
  □ Build 4×5 portal frame
  □ Ignite portal

PHASE 3 - Safety:
  □ Build cobblestone shelter around Nether portal
  □ Light area thoroughly
  □ Mark coordinates (write down)
  □ Create safe path from portal

READY: Enter Nether with full preparation
```

### Error Recovery Protocols

**Death Recovery**:
```
ON_DEATH:
    1. RESPAWN at bed (or world spawn)
    2. CHECK death coordinates (if visible)
    3. GATHER basic tools immediately:
       - Punch trees → Wood
       - Craft tools (wooden → stone quickly)
       - Gather food (kill animals)
    4. NAVIGATE to death location
       - Must arrive within 5 minutes (items despawn)
       - Avoid same danger that caused death
    5. COLLECT dropped items
    6. RETURN to base to reorganize
    7. ANALYZE death cause → Adjust strategy
```

**Lost in World**:
```
IF location_unknown:
    1. BUILD tall pillar (64 blocks vertical)
    2. PLACE torch on top
    3. NOTE current coordinates
    4. SCAN horizon for familiar landmarks:
       - Base structures
       - Distinctive terrain
       - Biome changes
    5. IF base visible:
       NAVIGATE directly
    6. IF base not visible:
       CHECK coordinates against known base location
       CALCULATE direction and distance
       BEGIN journey with waypoint markers every 50 blocks
```

**Tool Breaks During Task**:
```
ON_TOOL_BREAK:
    IF has_backup_tool:
        EQUIP backup
        CONTINUE task
        ADD "craft replacement" to queue
    ELIF can_craft_on_site:
        OPEN inventory crafting
        CRAFT basic tool
        CONTINUE task
    ELSE:
        MARK current location
        RETURN to base
        CRAFT proper tools
        RETURN to marked location
        RESUME task
```

## Conclusion for AI Agent

This guide provides comprehensive coverage of Minecraft mechanics, resources, and strategies. Key takeaways for optimal AI performance:

**Core Principles**:
1. **Safety First**: Health and hunger management override all goals
2. **Progression Path**: Wood → Stone → Iron → Diamond → Nether → End
3. **Resource Value**: Prioritize time-sensitive and rare materials
4. **Efficiency**: Batch similar tasks, minimize backtracking
5. **Preparation**: Always prepare beyond minimum requirements

**Decision-Making Hierarchy**:
```
1. Immediate Survival (health, hunger, safety)
2. Resource Security (tools, food, shelter)
3. Progression Goals (better equipment, new areas)
4. Optimization (farms, storage, efficiency)
5. Exploration (new biomes, structures, challenges)
```

**Success Metrics**:
- Survive first night: [SUCCESS] Basic shelter + light
- Reach Iron Age: [SUCCESS] Full iron tools by Day 3
- Find Diamonds: [SUCCESS] Diamond gear by Day 7-10
- Enter Nether: [SUCCESS] Portal built by Day 15
- Defeat Dragon: [SUCCESS] End dimension by Day 30+

**Remember**: Minecraft rewards patience, preparation, and iterative improvement. Each death teaches a lesson, each resource enables new capabilities, and every structure built makes survival easier. The game has no strict timeline—progress at a pace that ensures safety and thoroughness over speed and risk.