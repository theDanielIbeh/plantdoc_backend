from dataclasses import dataclass
import sys
from flask import Flask, abort, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.app_context().push()
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres@localhost:5432/plantdoc_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

@dataclass
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'{self.to_dict()}'
    
    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "password": self.password
        }

@dataclass
class Plant(db.Model):
    __tablename__ = "plant"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    image_url = db.Column(db.String(), nullable=False)
    botanical_name = db.Column(db.String(), unique=True, nullable=False)
    general_info = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'{self.to_dict()}'
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "image_url": self.image_url,
            "botanical_name": self.botanical_name,
            "general_info": self.general_info
        }

@dataclass
class Disease(db.Model):
    __tablename__ = "disease"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    class_index = db.Column(db.Integer, nullable=False)
    plant_id = db.Column(db.Integer, nullable=False)
    botanical_name = db.Column(db.String(), nullable=False)
    image_url = db.Column(db.String(), nullable=False)
    symptoms = db.Column(db.String(), nullable=False)
    cause = db.Column(db.String(), nullable=False)
    propagation = db.Column(db.String(), nullable=False)
    control = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f'{self.to_dict()}'
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "class_index": self.class_index,
            "plant_id": self.plant_id,
            "botanical_name": self.botanical_name,
            "image_url": self.image_url,
            "symptoms": self.symptoms,
            "cause": self.cause,
            "propagation": self.propagation,
            "control": self.control
        }

@dataclass
class History(db.Model):
    __tablename__ = "history"
    user_id = db.Column(db.Integer, nullable=False, primary_key=True)
    predicted_class_id = db.Column(db.Integer, nullable=False)
    local_url = db.Column(db.String(), unique=True, nullable=False)
    remote_url = db.Column(db.String(), nullable=False)
    date = db.Column(db.String(), nullable=False, primary_key=True)

    def __repr__(self):
        return f'{self.to_dict()}'
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "predicted_class_id": self.predicted_class_id,
            "local_url": self.local_url,
            "remote_url": self.remote_url,
            "date": self.date,
        }

db.create_all()

# plants = [
#     Plant(
#         id = 1,
#         name = "Tomato",
#         image_url="https://plantvillage-production-new.s3.amazonaws.com/image/1200/file/medium-2c50f2ab34ec579ecbd4b8348c3796e3.jpg",
#         botanical_name = "Lycopersicon esculentum",
#         general_info = "Tomato is an herbaceous annual in the family Solanaceae grown for its edible fruit. The plant can be erect with short stems or vine-like with long, spreading stems.\n\n" +
#         "The stems are covered in coarse hairs and the leaves are arranged spirally. The tomato plant produces yellow flowers, which can develop into a cyme of 3–12, and usually, a round fruit (berry) that is fleshy, smoothed skin, and can be red, pink, purple, brown, orange, or yellow in color.\n\n" +
#         "The tomato plant can grow 0.7–2 m (2.3–6.6 ft) in height and as an annual, is harvested after only one growing season. Tomato may also be referred to as the love apple and originates from South America.\n\n" +
#         "Tomatoes are native to South and Central America, but they are now grown all over the world.\n\n" +
#         "Tomatoes are one of Africa's most widely grown vegetable crops. They are grown for home consumption in almost every homestead's backyard across Sub-Saharan Africa.\n\n" +
#         "They are a good source of vitamins as well as a cash crop for smallholders and medium-scale commercial farmers. Tomatoes used as flavor enhancers in food are always in high demand, both fresh and processed."
#     )
# ]
# db.session.add_all(plants)
# db.session.commit()

# diseases = [
#     Disease(
#                 id = 1,
#                 name = "Early blight",
#                 class_index = 1,
#                 plant_id = 1,
#                 botanical_name = "Alternaria solani",
#                 image_url = "https://plantvillage-production-new.s3.amazonaws.com/image/1174/file/default-8f41d050e6c87d875b13a6bf63c6e202.jpg",
#                 symptoms = "Early blight symptoms start as oval shaped lesions with a yellow chlorotic region across the lesion; concentric leaf lesions may be seen on infected leaves; leaf tissue between veins is destroyed; severe infections can cause leaves to completely collapse; as the disease progresses leaves become severely blighted leading to reduced yield; tomato stems may become infected with the fungus leading to Alternaria stem canker; initial symptoms of of stem canker are the development of dark brown regions on the stem; stem cankers may enlarge to girdle the whole stem resulting in the death of the whole plant; brown streaks can be found in the vascular tissue above and below the canker region; fruit symptoms include small black v-shaped lesions at the shoulders of the fruit (the disease is also known black shoulder); lesions may also appear on the fruit as dark flecks with concentric ring pattern; fruit lesions can seen in the field or may develop during fruit transit to the market; the lesions may have a velvety appearance caused by sporulation of the fungus",
#                 cause = "Fungus",
#                 propagation = "Disease can spread rapidly after plants have set fruit; movement of air-borne spores and contact with infested soil are causes for the spread of the disease",
#                 control = "Apply appropriate fungicide at first sign of disease; destroy any volunteer solanaceous plants (tomato, potato, nightshade etc); practice crop rotation",
#             ),
#             Disease(
#                 id = 2,
#                 name = "Leaf Mold",
#                 class_index = 3,
#                 plant_id = 1,
#                 botanical_name = "Passalora fulva",
#                 image_url = "https://plantvillage-production-new.s3.amazonaws.com/image/63616/file/default-fcdcc0914dbf2813e91de329afb2af7c.jpg",
#                 symptoms = "The older leaves exhibit pale greenish to yellow spots (without distinguishable margins) on upper surface. Whereas the lower portion of this spots exhibit green to brown velvety fungal growth. As the disease progress the spots may coalesce and appear brown. The infected leaves become wither and die but stay attached to the plant. The fungus also infects flowers and fruits. The affected flowers become black and drop off. The affected fruit intially shows smooth black irregular area on the stem end but later it becomes sunken, leathery and dry.",
#                 cause = "Fungus",
#                 propagation = "The disease is favored by high relative humidity. Also a common disease in green house tomato crop.",
#                 control = "Grow available resistant varieties. Avoid leaf wetting and overhead application of water. Follow proper spacing to provide good air circulation around the plants. Remove the infected plant debris and burn them. If the disease is severe scary suitable fungicide.",
#             ),
#             Disease(
#                 id = 3,
#                 name = "Septoria Leaf Spot",
#                 class_index = 4,
#                 plant_id = 1,
#                 botanical_name = "Septoria lycopersici",
#                 image_url = "https://plantvillage-production-new.s3.amazonaws.com/image/632/file/default-12fb494e83390ef47bc24b4ac6950815.jpg",
#                 symptoms = "Symptoms may occur at any stage of tomato development and begin as small, water-soaked spots or circular grayish-white spots on the underside of older leaves; spots have a grayish center and a dark margin and they may colasece; fungal fruiting bodies are visible as tiny black specks in the center of spot; spots may also appear on stems, fruit calyxes, and flowers.",
#                 cause = "Fungus",
#                 propagation = "Spread by water splash; fungus overwinters in plant debris.",
#                 control = "Ensure all tomato crop debris is removed and destroyed in Fall or plowed deep into soil; plant only disease-free material; avoid overhead irrigation; stake plants to increase air circulation through the foliage; apply appropriate fungicide if necessary.",
#             ),
#             Disease(
#                 id = 4,
#                 name = "Target Spot",
#                 class_index = 6,
#                 plant_id = 1,
#                 botanical_name = "Corynespora cassiicola",
#                 image_url = "https://plantvillage-production-new.s3.amazonaws.com/image/63709/file/default-af946e9dfa8d58fc9035c811da13d461.jpg",
#                 symptoms = "The fungus infects all parts of plant. Infected leaves shows small, pinpoint, water soaked spots initially. As the disease progress the spots enlarge to become necrotic lesions with conspicuous concentric circles, dark margins and light brown centers. Whereas the fruits exhibit brown, slightly sunken flecks in the beginning but later the lesions become large pitted appearance.",
#                 cause = "Fungus",
#                 propagation = "The pathogen infects cucumber, pawpaw , ornamental plants, some weed species etc. The damaged fruits are susceptible for this disease.",
#                 control = "Remove the plant debris and burn them. Avoid over application of nitrogen fertilizer. If the disease is severe spray suitable fungicides.",
#             ),
#             Disease(
#                 id = 5,
#                 name = "Bacterial spot",
#                 class_index = 0,
#                 plant_id = 1,
#                 botanical_name = "Xanthomonas campestris pv. vesicatoria",
#                 image_url = "https://plantvillage-production-new.s3.amazonaws.com/image/4118/file/default-b533c30a34a8148266e60523a83461fd.jpg",
#                 symptoms = "Bacterial spot lesions starts out as small water-soaked spots; lesions become more numerous and coalesce to form necrotic areas on the leaves giving them a blighted appearance; of leaves drop from the plant severe defoliation can occur leaving the fruit susceptible to sunscald; mature spots have a greasy appearance and may appear transparent when held up to light; centers of lesions dry up and fall out of the leaf; blighted leaves often remain attached to the plant and give it a blighted appearance; fruit infections start as a slightly raised blister; lesions may have a faint halo which eventually disappears; lesions on fruit may have a raised margin and sunken center which gives the fruit a scabby appearance.",
#                 cause = "Bacterium",
#                 propagation = "Bacteria survive on crop debris; disease emergence favored by warm temperatures and wet weather; symptoms are very similar to other tomato diseases but only bacterial spot will cause a cut leaf to ooze bacterial exudate; the disease is spread by infected seed, wind-driven rain, diseased transplants, or infested soil; bacteria enter the plant through any natural openings on the leaves or any openings caused by injury to the leaves.",
#                 control = "Use only certified seed and healthy transplants; remove all crop debris from planting area; do not use sprinkler irrigation, instead water from base of plant; rotate crops.",
#             ),
#             Disease(
#                 id = 6,
#                 name = "Late blight",
#                 class_index = 2,
#                 plant_id = 1,
#                 botanical_name = "Phytophthora infestans",
#                 image_url = "https://plantvillage-production-new.s3.amazonaws.com/image/1187/file/default-7add4975438ae1ed96ee04b40bcb0cb8.jpg",
#                 symptoms = "Late blight affects all aerial parts of the tomato plant; initial symptoms of the disease appear as water-soaked green to black areas on leaves which rapidly change to brown lesions; fluffy white fungal growth may appear on infected areas and leaf undersides during wet weather; as the disease progresses, foliage becomes becomes shriveled and brown and the entire plant may die; fruit lesions start as irregularly shaped water soaked regions and change to greasy spots; entire fruit may become infected and a white fuzzy growth may appear during wet weather.",
#                 cause = "Oomycete",
#                 propagation = "Can devastate tomato plantings.",
#                 control = "Plant resistant varieties; if signs of disease are present or if rainy conditions are likely or if using overhead irrigation appropriate fungicides should be applied.",
#             ),
#             Disease(
#                 id = 7,
#                 name = "Tomato mosaic virus",
#                 class_index = 8,
#                 plant_id = 1,
#                 botanical_name = "Tomato mosaic virus (ToMV)",
#                 image_url = "https://plantvillage-production-new.s3.amazonaws.com/image/63694/file/default-0e281ebc682d3f01c011a93828688493.jpg",
#                 symptoms = "Symptoms can occur at any growth stage and any part of the plant can be affected; infected leaves generally exhibit a dark green mottling or mosaic; some strains of the virus can cause yellow mottling on the leaves; young leaves may be stunted or distorted; severely infected leaves may have raised green areas; fruit yields are reduced in infected plants; green fruit may have yellow blotches or necrotic spots; dark necrotic streaks may appear on the stems, petioles leaves and fruit.",
#                 cause = "Virus",
#                 propagation = "ToMV is a closely related strain of Tobacco mosaic virus (TMV), it enters fields via infected weeds, peppers or potato plants; the virus may also be transmitted to tomato fields by grasshoppers, small mammals and birds.",
#                 control = "Plant varieties that are resistant to the virus; heat treating seeds at 70°C (158°F) for 4 days or at 82–85°C (179.6–185°F) for 24 hours will help to eliminate any virus particles on the surface of the seeds; soaking seed for 15 min in 100 g/l of tri-sodium phosphate solution (TSP) can also eliminate virus particles - seeds should be rinsed thoroughly and laid out to dry after this treatment; if the virus is confirmed in the field, infected plants should be removed and destroyed to limit further spread; plant tomato on a 2-year rotation, avoiding susceptible crops such as peppers, eggplant, cucurbits and tobacco; disinfect all equipment when moving from infected areas of the field.",
#             ),
#             Disease(
#                 id = 8,
#                 name = "Tomato Yellow Leaf Curl disease",
#                 class_index = 7,
#                 plant_id = 1,
#                 botanical_name = "Tomato Yellow Leaf Curl Virus (TYLCV)",
#                 image_url = "https://plantvillage-production-new.s3.amazonaws.com/image/63702/file/default-41ffe47367c8058dd58d668669e7e677.jpg",
#                 symptoms = "The infected leaves become reduced in size, curl upward, appear crumpled and show yellowing of veins and leaf margins. The internodes become shorter and whole plant appear stunted and bushy. The whole plant stand erect with only upright growth. The flowers may not develop and drop off.",
#                 cause = "Virus",
#                 propagation = "The virus is transmitted by white flies and may cause 100 % yield loss if the plants infect at early stage of crop. The virus also infect other hosts like common bean, ornamental plants and several weed species.",
#                 control = "Grow available resistant varieties. Transplant only disease and whiteflies free seedlings. Remove the infected plants and burn them. Keep the field free from weeds. Use yellow sticky traps to monitor and control whiteflies. If the insect infestation is severe spray suitable insecticides.",
#             ),
#             Disease(
#                 id = 9,
#                 name = "Leafminers",
#                 class_index = -1,
#                 plant_id = 1,
#                 botanical_name = "Tuta absoluta",
#                 image_url = "https://plantvillage-production-new.s3.amazonaws.com/image/62538/file/default-64cefc6d20018775329221143a28779a.jpg",
#                 symptoms = "Thin, white, winding trails on leaves; heavy mining can result in white blotches on leaves and leaves dropping from the plant prematurely; early infestation can cause fruit yield to be reduced; adult leafminer is a small black and yellow moth which lays its eggs in the leaf; larvae hatch and feed on leaf interior.",
#                 cause = "Insect",
#                 propagation = "Origin and distribution of Tuta absoluta: This species is originated in South American countries. Later the insect spread to Spain (2006), France, Italy, Greece, Malta, Morocco, Algeria, Libya and Turkey in following years. Further the insect has been identified in Syria, Lebanon, Jordan, Iraq, Iran, Saudi Arabia, Yemen, Oman and the rest of the Gulf states. In Africa it spreads from Egypt to Sudan, South Sudan, Ethiopia, Uganda, Kenya and Tanzania (in East) and to Senegal and Nigeria through the west. (It spread through infested fruits and packaging materials) Life cycle: Mature larvae drop from leaves into soil to pupate; entire lifecycle can take as little as 2 weeks in warm weather; insect may go through 7 to 12 generations per year. Yield loss: If unchecked, insect will cause 100% yield loss. The larvae feeds on apical buds, tender new leaflets, flowers, and green fruits which make it a serious pest in tomato. Host Range: This insect also attacks other solanaceous crops like potato, eggplant, pepino and tobacco. It is also reported on many solanaceous weeds.",
#                 control = "Leafminer natural enemies normally keep populations under control; check transplants for signs of leafminer damage prior to planting; remove plants from soil immediately after harvest if making new plantings in same place or close by; keep the field free from weeds especially Solanum, Datura, Nicotiana; use pheromone traps and white sticky traps to monitor and control insect;only use insecticides when leafminer damage has been identified as unnecessary spraying will also reduce populations of their natural enemies.",
#             ),
#             Disease(
#                 id = 10,
#                 name = "Spider mites (Two-spotted spider mite)",
#                 class_index = 5,
#                 plant_id = 1,
#                 botanical_name = "Tetranychus urticae",
#                 image_url = "https://plantvillage-production-new.s3.amazonaws.com/image/63671/file/default-b987ce4b9e1adb0dc4278c5b7266e90b.jpg",
#                 symptoms = "Leaves stippled with yellow; leaves may appear bronzed; webbing covering leaves; mites may be visible as tiny moving dots on the webs or underside of leaves, best viewed using a hand lens; usually not spotted until there are visible symptoms on the plant; leaves turn yellow and may drop from plant.",
#                 cause = "Arachnid",
#                 propagation = "Spider mites thrive in dusty conditions; water-stressed plants are more susceptible to attack.",
#                 control = "In the home garden, spraying plants with a strong jet of water can help reduce buildup of spider mite populations; if mites become problematic apply insecticidal soap to plants; certain chemical insecticides may actually increase mite populations by killing off natural enemies and promoting mite reproduction.",
#             )
# ]
# db.session.add_all(diseases)
# db.session.commit()

def get_all_users():
    all_users=User.query.all()
    users_list = [user.to_dict() for user in all_users]
    return users_list

@app.route("/")
def index():
    return "PlantDoc!!!"

@app.route("/users/create", methods=["POST"])
def create_user():
    error = False
    try: 
        first_name = request.get_json()['first_name']
        last_name = request.get_json()['last_name']
        email = request.get_json()['email']
        password = request.get_json()['password']

        hashed_password = generate_password_hash(password)

        # Check if user exists
        if User.query.filter_by(email=email).first():
            return jsonify({"message": "Email already exists"}), 409
       
        # Add user to db
        user = User(first_name=first_name, last_name=last_name, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        # Return added user
        added_user = [user.to_dict() for user in User.query.filter_by(email=email).all()]
        return jsonify({"message": "success", "data" : added_user})
    except SQLAlchemyError as e:
        db.session.rollback()
        print(e)
        return jsonify({"message": "Database error", "error": str(e)}), 500

    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500     

@app.route("/login", methods=["POST"])
def login():
    try: 
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if user is None:
            return jsonify({"message": "Unregistered email"}), 404
        
        stored_password_hash = user.password

        if stored_password_hash is None or not check_password_hash(stored_password_hash, password):
            return jsonify({"message": "Wrong password"}), 401

        # Return added user
        added_user = [user.to_dict()]
        return jsonify({"message": "success", "data" : added_user})
        
    except SQLAlchemyError as e:
        db.session.rollback()
        print(e)
        return jsonify({"message": "Database error", "error": str(e)}), 500

    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500

@app.route("/users", methods=["GET"])
def get_users():
    print(get_all_users())
    return jsonify({"message": "success", "data" : get_all_users()})

@app.route("/plants", methods=["GET"])
def get_plants():
    all_plants=Plant.query.all()
    plants_list = [plant.to_dict() for plant in all_plants]
    return jsonify({"message": "success", "data" : plants_list})

@app.route("/diseases", methods=["GET"])
def get_diseases():
    all_diseases=Disease.query.all()
    diseases_list = [disease.to_dict() for disease in all_diseases]
    return jsonify({"message": "success", "data" : diseases_list})

@app.route("/history", methods=["GET"])
def get_user_history():
    try:
        user_id = request.args.get('user_id')

        user_history = History.query.filter_by(user_id=user_id).all()
        history_data = [history.to_dict() for history in user_history]

        return jsonify({"message": "success", "data": history_data})

    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500

@app.route("/history/create", methods=["POST"])
def create_history():
    error = False
    try: 
        user_id = request.get_json()['user_id']
        predicted_class_id = request.get_json()['predicted_class_id']
        local_url = request.get_json()['local_url']
        remote_url = request.get_json()['remote_url']
        date = request.get_json()['date']
       
        # Add user to db
        history = History(user_id = user_id,
                       predicted_class_id = predicted_class_id,
                       local_url = local_url,
                       remote_url = remote_url,
                       date = date)
        
        db.session.add(history)
        db.session.commit()

        # Return added user
        added_history = [history.to_dict() for history in History.query.filter_by(user_id=user_id).filter_by(date=date).all()]
        return jsonify({"message": "success", "data" : added_history})
    except SQLAlchemyError as e:
        db.session.rollback()
        print(e)
        return jsonify({"message": "Database error", "error": str(e)}), 500

    except Exception as e:
        print(e)
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500   