#!/usr/bin/env python
# CODE FROM DOMI, FUNCTIONS ROS = TRANSLATED IN THE NOTEBOOK
from pyquaternion import Quaternion
import numpy as np
from numpy import linalg as LA

# hardcoded tool and tooltip rotation and position in form [qx,qy,qz,qw,tx,ty,tz]
def get_transformation_matrix(tool):
    tools_geom = {
        "tweezers": {
            "marker_top": [0.294683893, -0.381338443, 0.804004129, -0,348218245, 0.02071305, 0.315910506, 0.109691984, 1],     # the one from the fixed marker for top measurement
            "marker_tip": [-0.934570634, -0.199016144, -0.27846308, -0.09708261, -0.084385462, 0.322035324, 0.247498733, 1],     # the one from the fixed marker for tip measurement
            "top":  [-0.957423623, 0.232203992, 0.045994597, -0.164969258, -0.957423623, 0.064656852, 0.30305547, 0.118855763,1],    # marker to rpz top
            "tip":  [-0.982271943, 0.074956687, 0.087323391, -0.147737227, 0.009193922, 0.29774011, 0.185825182, 1]      # marker to rpz tip
        
        },
        "holder":  {
            "marker_top": [-0.464328416, -0.824174638, 0.259212521, 0.194345126, -0.028731799, 0.37167886, 0.187163421, 1],
            "marker_tip": [-0.607490434, -0.786474846, 0.065937201, 0.066721948, -0.09777691, 0.273007487, 0.129043679, 1],
            "top": [-0.999966857, -0.005855143, 0.001344358, -0.004240937, 0.038997519, 0.391597069, 0.185368827, 1],
            "tip":  [-0.998836327, 0.047065242, 0.006078749, -0.008203204, -0.003049673, 0.288822714, 0.204019114, 1]

        },        
        "scissors": {
            "marker_top": [-0.042840319, -0.680377306, -0.566847792, 0.46252974, -0.081934339, 0.350532647, 0.195744726, 1],
            "marker_tip": [0.006243079, -0.843461761, -0.292836166, 0.450291385, 0.091436198, 0.357834012, 0.119615055, 1],
            "top": [-0.998896472, -0.011071288, 0.035124272, -0.028830308, -0.010444363, 0.372744524, 0.189865359, 1],
            "tip": [-0.174518025, -0.309318304, 0.422878875, 0.833678217, 0.052825127, 0.265624369, 0.148519055, 1]
        }
    }


    #print(tool)
    marker_top_quaternion = Quaternion(tools_geom[tool]["marker_top"][:4])  #Return homogeneous rotation matrix from quaternion. = on calcule la matrice de rotation qui correspond aux quaternions du tool (chiffres en haut) #ATTENTION: normalise le quaternion a 1 donc pas exactemetn meme valeurs
    T_marker_top_fixed = marker_top_quaternion.transformation_matrix         # deja en 4*4 matrix
    
    marker_top_translation_vector = np.array((tools_geom[tool]["marker_top"][-4:])) #Return matrix to translate by direction vector = on calcule la matrice de translation qui correspond aux positions du tool (chiffres en haut)
    T_marker_top_fixed[:,-1] = marker_top_translation_vector       #matrice de transformation pour passer de mon objet au centre du reference frame à sa position actuelle (marker de l'outils)
    
    marker_tip_quaternion = Quaternion(tools_geom[tool]["marker_tip"][:4])  #Return homogeneous rotation matrix from quaternion. = on calcule la matrice de rotation qui correspond aux quaternions du tool (chiffres en haut) #ATTENTION: normalise le quaternion a 1 donc pas exactemetn meme valeurs
    T_marker_tip_fixed = marker_tip_quaternion.transformation_matrix         # deja en 4*4 matrix
    
    marker_tip_translation_vector = np.array((tools_geom[tool]["marker_tip"][-4:])) #Return matrix to translate by direction vector = on calcule la matrice de translation qui correspond aux positions du tool (chiffres en haut)
    T_marker_tip_fixed[:,-1] = marker_tip_translation_vector       #matrice de transformation pour passer de mon objet au centre du reference frame à sa position actuelle (marker de l'outils)
        
    top_quaternion = Quaternion(tools_geom[tool]["top"][:4])  #Return homogeneous rotation matrix from quaternion. = on calcule la matrice de rotation qui correspond aux quaternions du tool (chiffres en haut) #ATTENTION: normalise le quaternion a 1 donc pas exactemetn meme valeurs
    T_top = top_quaternion.transformation_matrix         # deja en 4*4 matrix
    
    top_translation_vector = np.array((tools_geom[tool]["top"][-4:])) #Return matrix to translate by direction vector = on calcule la matrice de translation qui correspond aux positions du tool (chiffres en haut)
    T_top[:,-1] = top_translation_vector       #matrice de transformation pour passer de mon objet au centre du reference frame à sa position actuelle (marker de l'outils)
    
    tip_quaternion = Quaternion(tools_geom[tool]["tip"][:4]) #matrice de rotation des quaternions du tip #ATTENTION: normalise le quaternion a 1 donc pas exactemetn meme valeurs
    T_tip = tip_quaternion.transformation_matrix
  
    tip_translation_vector = np.array((tools_geom[tool]["tip"][-4:])) #-4 car 4 dernieres valeurs
    T_tip[:,-1] = tip_translation_vector       #matrice de transformation pour passer de mon objet au centre du reference frame à sa position actuelle (tip de l'outils)
    
    T_marker_top_fixed_inv = LA.inv(T_marker_top_fixed)  
    T_marker_tip_fixed_inv = LA.inv(T_marker_tip_fixed)  
    #T_marker_inv = np.identity(4)
    #T_marker_inv[:3, :3] = LA.inv(T_tool[:3, :3])
    #T_marker_inv[:3, -1] = -T_tool_inv[:3, :3].dot(T_tool[:3, -1]) #msimplement une autre maniere de la calculer l'inverse !!!!!!!!!!!!!!
   
    
# ORIGIN TO TOOL, BASED ON MARKER POSITION
   
    T_marker_top = T_marker_top_fixed_inv.dot(T_top) #Matrice mTtop = marker to top
    q_marker_top = Quaternion(matrix = T_marker_top)

    
# ORIGIN TO TIP, BASED ON MARKER POSITION
     
    T_marker_tip = T_marker_tip_fixed_inv.dot(T_tip) #Matrice mTtip = marker to tip
    q_marker_tip = Quaternion(matrix = T_marker_tip)
    
    return(T_marker_top, T_marker_tip)