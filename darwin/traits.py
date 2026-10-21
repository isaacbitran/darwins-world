"""Hand-curated trait pool. Each line: phrase | short label for species names | feature tags.
A creature has one trait per slot (8 slots). Tags are used only for measurement and drawing, never shown to Jev."""

RAW = {
"size": """
tiny, the size of an ant|ant-sized|small
tiny, the size of a beetle|beetle-sized|small
the size of a bumblebee|bee-sized|small
the size of a large spider|spider-sized|small
the size of a mouse|mouse-sized|small
the size of a shrew|shrew-sized|small
the size of a sparrow|sparrow-sized|small
the size of a frog|frog-sized|small
the size of a hamster|hamster-sized|small
the size of a small lizard|lizard-sized|small
the size of a rat|rat-sized|small
the size of a squirrel|squirrel-sized|small
the size of a pigeon|pigeon-sized|small
the size of a guinea pig|guinea-pig-sized|small
the size of a rabbit|rabbit-sized|mid
the size of a house cat|cat-sized|mid
the size of a crow|crow-sized|mid
the size of a ferret|ferret-sized|mid
the size of a fox|fox-sized|mid
the size of a small dog|dog-sized|mid
the size of a raccoon|raccoon-sized|mid
the size of a goose|goose-sized|mid
the size of a badger|badger-sized|mid
the size of a beaver|beaver-sized|mid
the size of a coyote|coyote-sized|mid
the size of a goat|goat-sized|mid
the size of a large dog|hound-sized|mid
the size of a sheep|sheep-sized|mid
the size of a wolf|wolf-sized|big
the size of a deer|deer-sized|big
the size of a human|human-sized|big
the size of a seal|seal-sized|big
the size of a lion|lion-sized|big
the size of a large pig|boar-sized|big
the size of a horse|horse-sized|big
the size of a bear|bear-sized|big
the size of a cow|cow-sized|big
the size of a walrus|walrus-sized|big
the size of a rhinoceros|rhino-sized|big
the size of an elephant|elephant-sized|big
""",
"covering": """
thick, dense, insulating fur|thick-furred|insul fur
a long shaggy double coat of fur|shaggy|insul fur
a woolly undercoat beneath long guard hairs|woolly|insul fur
short sleek fur|sleek-furred|fur
thin, sparse fur|thin-furred|fur bare
soft velvety fur|velvet-furred|fur
spiky quills mixed into coarse fur|quilled|fur armor
a thick layer of blubber under smooth skin|blubbered|insul blubber smooth
a heavy blubber layer under a short dense pelt|blubber-pelted|insul blubber fur
a fatty insulating hide|fat-hided|insul blubber
thick downy feathers|down-feathered|insul feathers
sleek waterproof feathers|oily-feathered|feathers smooth
bright display feathers|plumed|feathers
short stiff feathers|stiff-feathered|feathers
loose fluffy feathers|fluffy|feathers
small dry overlapping scales|dry-scaled|scales
thick armored scales|armor-scaled|scales armor
smooth glossy scales|glossy-scaled|scales smooth
rough bumpy scales|rough-scaled|scales
heat-reflecting pale scales|reflective-scaled|scales heat
hard bony plates along the back|plated|armor
a domed hard shell it can hide inside|shelled|armor shell
a heavy spiral shell|spiral-shelled|armor shell
a flexible leathery shell|leather-shelled|armor shell
a segmented hard exoskeleton|exoskeletal|armor
a thin chitin exoskeleton|chitinous|armor
a hairy exoskeleton|hairy-shelled|armor
bare wrinkled skin|bare-skinned|bare
thin moist skin|moist-skinned|bare smooth
slimy mucus-covered skin|slimy|bare smooth
smooth rubbery skin|rubbery|bare smooth
thick leathery hide|leathery|bare
tough hairless hide with thick calluses|callused|bare
warty toxic skin|warty|bare
translucent jelly-like skin|glassy|bare smooth
paper-thin skin that shows its veins|thin-skinned|bare
coarse bristly hair|bristly|fur
a mane of long hair around the neck|maned|fur
fine waterproof fur like an otter's|otter-furred|fur insul smooth
fur that sheds completely in summer|molting|fur
a thick mat of moss-like hair|mossy|fur
sticky skin covered in fine dust|dusty|bare
spines like a sea urchin|spiny|armor
waxy waterproof skin|waxy|bare water
a crust of mineral deposits on its skin|crusted|armor heat
loose folds of heavy skin|fold-skinned|bare
small soft scales like a fish|fish-scaled|scales smooth
thick sand-colored hair that shades the skin|sun-haired|fur heat
a coat of hollow hairs that trap warm air|hollow-haired|insul fur
patchy, mangy fur|mangy|fur bare
""",
"color": """
pure snow white|snow-white|white
creamy off-white|cream|white pale
pale silver-grey|silver|white pale
white in winter and brown in summer|seasonal|white
pale sandy tan|sand-colored|sandy pale
dusty yellow-ochre|ochre|sandy
reddish desert brown|rust-brown|sandy
speckled beige and tan|speckled|sandy
pitch black|black|dark
dark charcoal grey|charcoal|dark
deep midnight blue|midnight|dark
sooty brown-black|sooty|dark
dark chocolate brown|brown|dark
leaf green|leaf-green|green
mottled moss green|moss-green|green
emerald green with yellow spots|emerald|green bright
olive brown|olive|green
bright scarlet red|scarlet|bright
vivid orange and black stripes|tiger-striped|bright
electric blue|electric-blue|bright
neon yellow|neon|bright
iridescent purple|iridescent|bright
pink|pink|bright
rainbow-patterned|rainbow|bright
grey with dark spots|spotted|
tawny gold|golden|sandy
reddish orange|fox-red|bright
blue-grey like the sea|sea-grey|sea
dark blue on top and white underneath|countershaded|sea
silvery like a fish|silvery|sea pale
transparent, nearly invisible|clear|pale
pale ghostly white without any pigment|unpigmented|white pale cave
dull mud brown|mud-brown|
black and white stripes|zebra-striped|
ash grey like volcanic rock|ash-grey|dark
glossy jet black with red markings|black-and-red|dark bright
""",
"diet": """
eats grass and leaves|grazer|herb
eats fruit and nuts|fruit-eater|herb
eats seeds|seed-eater|herb
eats tree bark and twigs|browser|herb
eats roots and tubers|root-digger|herb
eats moss and lichen|lichen-eater|herb
drinks flower nectar|nectar-sipper|herb
eats algae and seaweed|kelp-grazer|herb sea
eats cactus and succulent plants|cactus-eater|herb
eats insects|insect-eater|carn small_prey
eats worms and grubs|grub-eater|carn small_prey
eats small rodents|mouser|carn
eats fish|fish-eater|carn sea
eats shellfish and crabs|crab-eater|carn sea
filters plankton from the water|filter-feeder|filter sea
eats carrion and scraps|scavenger|scav
eats anything it can find|omnivore|omni
hunts large animals much bigger than itself|big-game hunter|carn
hunts other creatures of its own size|hunter|carn
eats eggs|egg-thief|carn
drinks blood|bloodsucker|carn
eats fungi and mushrooms|fungus-eater|herb cave
eats bacteria growing on rocks|rock-grazer|herb cave
eats dead plant matter and dung|detritivore|scav
eats bones|bone-cruncher|scav
eats seals and large fish|seal-hunter|carn sea
eats bats and cave insects|cave-hunter|carn cave
eats other predators|apex predator|carn
eats ants and termites|anteater|carn small_prey
eats snails|snail-eater|carn small_prey
eats mineral-rich clay|clay-eater|herb
eats microbes from hot springs|vent-feeder|herb heat
""",
"locomotion": """
runs fast on four long legs|sprinter|run
walks slowly on four stout legs|plodder|walk
walks on two strong legs|biped|walk
hops on powerful hind legs|hopper|run
gallops in bursts|galloper|run
climbs trees with gripping claws|tree-climber|climb
swings between branches with long arms|brachiator|climb
glides between trees on skin flaps|glider|climb fly
flies on feathered wings|flier|fly
flies on leathery bat wings|bat-winged|fly
hovers with fast-beating wings|hoverer|fly
soars on wide wings for hours|soarer|fly
swims with fins and a tail fluke|finned|aquatic
swims with webbed feet|web-footed|aquatic semi
dives deep with flippers|flippered|aquatic
swims by jet propulsion|jet-swimmer|aquatic
paddles on the water surface|paddler|aquatic semi
digs tunnels with shovel-like claws|burrower|burrow
burrows through sand|sand-swimmer|burrow sand
slithers without legs|slitherer|crawl
crawls on many small legs|crawler|crawl
inches along on a muscular foot|slider|crawl
scuttles sideways on jointed legs|scuttler|crawl
clings to rock walls with suction pads|wall-clinger|climb cave
walks on wide snowshoe feet|snowshoe|walk snow
skates on ice with grippy pads|ice-walker|walk snow
leaps between rocks like a goat|rock-hopper|climb
rolls into a ball and tumbles|roller|crawl
walks on stilt-like legs over hot ground|stilt-walker|walk heat
drifts with the current|drifter|aquatic
moves by jumping very high|jumper|run
crawls along the sea floor on stiff fins|bottom-walker|aquatic
""",
"activity": """
active only at night|nocturnal|noct
active at dawn and dusk|crepuscular|crep
active during the day|diurnal|day
active during the hottest part of the day|sun-loving|day heat
active in short bursts day and night|restless|
active only in the cool early morning|dawn-active|crep
sleeps through most of the day and night|sleepy|
active year-round regardless of light|tireless|
active only during rain|rain-active|
active in total darkness|dark-dwelling|noct cave
""",
"behavior": """
lives in large herds|herding|social
hunts in coordinated packs|pack-hunting|social carn_b
lives alone and defends a territory|solitary|
waits motionless and ambushes prey|ambush|carn_b
stalks prey silently|stalking|carn_b
chases prey over long distances|pursuit|carn_b
builds burrows and hides underground|burrowing|burrow
digs a deep den to wait out bad weather|denning|burrow
hibernates through the winter|hibernating|cold
sleeps through dry seasons buried in mud|aestivating|water
stores food in hidden caches|hoarding|
migrates long distances each season|migratory|
huddles together for warmth|huddling|social cold
plays dead when attacked|death-feigning|defense
sprays a foul-smelling liquid when threatened|stink-spraying|defense
has a venomous bite|venomous|defense carn_b
is poisonous to eat|toxic|defense
camouflages perfectly against its surroundings|camouflaged|defense
mimics a dangerous animal|mimic|defense
lives in trees and rarely touches the ground|arboreal|climb
nests in cliffs high above the ground|cliff-nesting|
lays many eggs and abandons them|egg-scattering|
raises one baby at a time with great care|devoted|
gives birth to large litters often|prolific|
builds dams and lodges in water|dam-building|aquatic
hides inside its shell when threatened|turtling|defense armor
flees at the first sign of danger|skittish|defense
fights fiercely with horns|horned|defense
lives in a colony underground|colonial|burrow social
follows larger predators to steal kills|thieving|scav
fishes by diving from above|plunge-diving|sea
spends most of its life underwater|underwater|aquatic
basks in the sun to warm up|basking|heat
shelters under rocks during the heat of the day|shade-seeking|heat water
dig for water underground|water-digging|water burrow
drinks dew from its own body|dew-drinking|water
digs through snow to reach food|snow-digging|cold
lives in total darkness in deep caves|cave-dwelling|cave
squeezes into narrow cracks|crevice-hiding|cave
uses tools like sticks and stones|tool-using|smart
is very curious and learns quickly|clever|smart
communicates with loud calls|loud|social
mates for life|monogamous|
dances to attract mates|courting|
grooms others in its group|grooming|social
""",
"physiology": """
needs to drink water several times a day|thirsty|wet
almost never needs to drink water|water-saving|water
gets all its water from food|food-hydrated|water
stores water in a hump of fat|camel-humped|water
stores fat to survive long famines|fat-storing|cold
has a very slow metabolism and needs little food|slow-burning|low_food
has a fast metabolism and must eat constantly|fast-burning|high_food
has antifreeze in its blood|antifreeze|cold
has small ears and a short tail to save heat|compact|cold
has huge ears that shed heat|big-eared|heat
pants and sweats to stay cool|sweating|heat wet
survives body temperatures above 45 C|heat-proof|heat
breathes through gills|gilled|aquatic
breathes air and holds its breath for an hour|deep-breath|aquatic semi
breathes through its skin|skin-breathing|wet
cannot survive out of water|water-bound|aquatic
has keen night vision|night-eyed|noct
is completely blind|blind|cave
navigates by echolocation|echolocating|cave noct
feels vibrations through long whiskers|whiskered|cave
has an excellent sense of smell|keen-nosed|
has eyes on stalks that see all directions|stalk-eyed|
sees heat with pit organs|heat-sensing|noct
glows in the dark|glowing|cave bright
senses electric fields in water|electric-sensing|aquatic
can go months without eating|starvation-proof|low_food
gets drunk on fermented fruit|fruit-loving|
regrows lost limbs|regenerating|
has thick padded feet that resist hot sand|pad-footed|heat sand
has fur-covered feet for walking on snow|snow-footed|cold snow
has a long sticky tongue|sticky-tongued|
has huge crushing jaws|big-jawed|carn_b
has razor-sharp teeth and claws|clawed|carn_b
has no teeth at all|toothless|
has a beak strong enough to crack nuts|beaked|
has a pouch for carrying young|pouched|
can change color to match its background|color-changing|defense
is immune to most snake venom|venom-proof|
tolerates toxic volcanic gases|gas-tolerant|volcanic
lives on very little oxygen|low-oxygen|cave volcanic
has kidneys that make almost dry urine|dry-kidneyed|water
loses heat quickly through thin skin|heat-leaking|heat_loss
cannot tolerate cold at all|cold-blooded|cold_weak
is cold-blooded and slows down in the cold|sluggish|cold_weak
is warm-blooded|warm-blooded|
has dense heavy bones for diving|dense-boned|aquatic
has light hollow bones|hollow-boned|fly
has strong lungs for high altitude|big-lunged|
""",
}

EXTRA = {
"covering": """
a thick pelt of white fur with black skin underneath|polar-pelted|insul fur
a short waterproof coat over a fat layer|sealskinned|insul blubber smooth fur
soft fluffy fur that traps air|fluffy-furred|insul fur
a coat of long wiry hair|wiry|fur
a hard beetle-like carapace|carapaced|armor
scaly armored plates like a pangolin|pangolin-plated|armor scales
a thin layer of short velvet hair|velvet-haired|fur
a heavy shell covered in barnacles|barnacled|armor shell sea
spiky armor around its head|spike-crowned|armor
a coat of feathers that looks like fur|feather-furred|feathers insul
smooth skin with a thin fat layer|smooth-skinned|bare smooth
loose shaggy fur that tangles in branches|tangle-furred|fur
""",
"color": """
pale lemon yellow|lemon|bright
warm cinnamon brown|cinnamon|sandy
cobalt blue with white bellies|cobalt|sea
bark brown with lichen spots|bark-colored|green
deep forest green|forest-green|green
black with glowing blue spots|starry|dark bright
copper red like hot embers|ember-red|bright
grey-brown like dry grass|grass-colored|sandy
white with black ear tips|ermine|white
blotchy grey and white like snow on rock|snow-mottled|white
red with white spots|toadstool|bright
bluish white like ice|ice-blue|white pale
""",
"diet": """
eats carrion frozen in the snow|ice-scavenger|scav cold
eats krill and tiny shrimp|krill-eater|filter sea
eats squid|squid-eater|carn sea
eats jellyfish|jelly-eater|carn sea
eats leaves high in the canopy|leaf-eater|herb
eats flowers and pollen|flower-eater|herb
eats frogs and lizards|lizard-eater|carn
eats birds and their chicks|bird-catcher|carn
eats beetles and scorpions|scorpion-eater|carn small_prey
eats dry grass seeds blown by the wind|wind-seed-eater|herb
eats termites from mounds|termite-eater|carn small_prey
eats spiders|spider-eater|carn small_prey
eats sea urchins|urchin-eater|carn sea
eats ferns|fern-eater|herb
eats water plants|pond-grazer|herb
eats ash-covered moss|ash-grazer|herb volcanic
eats grazing herd animals|herd-hunter|carn
eats fallen fruit on the forest floor|fruit-forager|herb
""",
"locomotion": """
swims with long flexible fins like an eel|eel-like|aquatic
swims fast with a torpedo-shaped body|torpedo|aquatic
waddles on land and swims with flippers|waddler|aquatic semi walk
pulls itself along with its front claws|clawcrawler|crawl
climbs cliffs with hooked claws|cliff-climber|climb
leaps from branch to branch|leaper|climb
runs on two long legs like an ostrich|strider|run
bounds through deep snow|snow-bounder|walk snow
digs into soft mud|mud-digger|burrow
tunnels through soil like a mole|tunneler|burrow
walks upside down on cave ceilings|ceiling-walker|climb cave
floats with a gas bladder|floater|aquatic
skims across water on its feet|water-runner|semi
flies short distances in bursts|flutterer|fly
""",
"activity": """
active through the long polar night|night-proof|noct cold
active only at high tide|tidal|sea
active at midday when prey basks|noon-hunting|day
active mostly in the winter|winter-active|cold
active only on cool cloudy days|cloud-active|
""",
"behavior": """
travels in schools|schooling|social aquatic
keeps its eggs inside its body until they hatch|live-bearing|
lays eggs in the sand|sand-nesting|sand
builds nests out of leaves high in trees|canopy-nesting|climb
hunts from the water's edge|shore-hunting|semi
hides in burrows during the day|day-hiding|burrow noct
travels great distances to find water|water-seeking|water
lives near hot springs for warmth|vent-dwelling|heat volcanic
uses its tail to grip branches|prehensile|climb
spins webs to catch prey|web-spinning|carn_b
hides under snow in tunnels|snow-tunneling|cold burrow
breaks the ice to fish|ice-fishing|cold sea
hunts by sound in the dark|ear-hunting|cave noct carn_b
digs for buried roots|root-digging|burrow
lives in mixed flocks with birds|flocking|social
dives under the waves to escape|wave-diving|aquatic
rolls in dust to keep off parasites|dust-bathing|
wallows in mud to stay cool|wallowing|heat wet
stands still for hours to save energy|statue-still|low_food
digs pits to trap prey|pit-trapping|carn_b
""",
"physiology": """
has a thick layer of fat that keeps it warm|fat-insulated|cold insul
has a tiny, efficient heart that saves energy|slow-hearted|low_food
can slow its heart and sleep for months|torpid|cold low_food
has nostrils that close underwater|seal-nosed|aquatic semi
has huge eyes for seeing in dim light|big-eyed|noct
has no eyes at all|eyeless|cave
cools its blood through its horns|horn-cooled|heat
has a long neck for reaching high leaves|long-necked|
has a waterproof nose that filters sand|sand-nosed|sand
has salt glands to drink seawater|salt-glanded|sea
can survive being frozen solid|freeze-proof|cold
has very long legs that keep its body off hot ground|long-legged|heat
has webbed toes|web-toed|semi
needs warm sunlight every day|sun-dependent|cold_weak
cannot swim|non-swimmer|
has heat-proof skin like asbestos|fireproof|heat volcanic
breathes through a tiny blowhole on its head|blowholed|aquatic
has sensitive antennae|antennaed|cave
has a very long lifespan|long-lived|
reproduces very quickly|fast-breeding|
""",
}
for _s, _txt in EXTRA.items():
    RAW[_s] = RAW[_s].rstrip() + "\n" + _txt.strip() + "\n"

SLOTS = list(RAW.keys())
POOL = []          # list of dicts: id, slot, phrase, label, tags
BY_SLOT = {s: [] for s in SLOTS}
for s in SLOTS:
    for line in RAW[s].strip().splitlines():
        phrase, label, tags = (x.strip() for x in line.split("|"))
        t = {"id": len(POOL), "slot": s, "phrase": phrase, "label": label, "tags": tags.split()}
        POOL.append(t); BY_SLOT[s].append(t["id"])

def describe(genome):
    """English description of a creature for Jev. genome = tuple of trait ids, one per slot."""
    p = [POOL[i]["phrase"] for i in genome]
    return (f"A creature {p[0]}, covered in {p[1]}, colored {p[2]}. It {p[3]}, {p[4]}, and is {p[5]}. "
            f"It {p[6]}, and {p[7]}.")

if __name__ == "__main__":
    print(len(POOL), {s: len(v) for s, v in BY_SLOT.items()})
