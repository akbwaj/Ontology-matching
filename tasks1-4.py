#import all required files
from owlready2 import *
import json
import os
#import logging

#path: location of scientific articles
path = "./data"
path_for_newFiles = "./data_modified"

def task1_loadOntology(ontology_name="doid.owl"):
	"""
	This function loads the disease ontology and returns a list of disease objects with DOID as the identifier.
	"""
	ontology = get_ontology(ontology_name)
	try:
		ontology.load()
	except owlready2.base.OwlReadyOntologyParsingError:
		ontology = ontology.load()

	print("******** Task 1: Ontology loaded, generating infoOfDiseases ********\n")

	infoOfDiseases = [item for item in ontology.classes()]
	return infoOfDiseases #[DOID_123,DOID_997...]

infoOfDiseases = task1_loadOntology()

def task2_3_extractLinkEntities(infoOfDiseases):
	"""
	This function extracts scientific entities from articles and links them with entities in the ontology.
	"""
    
    #map disease names (and synonyms) to index location in list infoOfDisease
	map_labelToLocation = {}
	for i,each in enumerate(infoOfDiseases):
		#print(i,each)
		label = each.label[0]
		map_labelToLocation[label] = i

		try:
			synonyms = each.hasExactSynonym
			#print(synonyms)
			if synonyms:
				for synonym in synonyms:
					map_labelToLocation[synonym] = i
		except:
			#print(f'Object {each} does not have synonym')
			continue
            
	print("***** Task 2: Label to index location dictionary created  *****\n")
    
    #extracted_labels stores all extracted labels in each document with title as key - to be used in next task
	extracted_labels = {}
	for filename in os.listdir(path):
		if filename.endswith(".json"):
			with open(os.path.join(path,filename),"r") as article:
				article = json.load(article)
				title = article['metadata']['title']
				article = str(article)
				for label in map_labelToLocation.keys():
					if label in article:
                            #if title exists then append labels, else create a new key/title
							extracted_labels[title] = extracted_labels.get(title,[])+[label]
                            #add the DOID identifier to the label
							article = article.replace(label,(label +' <'+ infoOfDiseases[map_labelToLocation[label]].get_name(infoOfDiseases[map_labelToLocation[label]]) +'> '))
				with open(os.path.join(path_for_newFiles,filename),'w') as file:
					s = json.dump(article,file,indent=4,separators=(',', ': '))
				#print(f"******* Written {filename} ********* ")
	print(f"******* All files updated with DOID entries *******")	

	return (extracted_labels,map_labelToLocation,infoOfDiseases)

extracted_labels,map_labelToLocation,infoOfDiseases = task2_3_extractLinkEntities(infoOfDiseases)

def task4_extractRelationship(extracted_labels,map_labelToLocation,infoOfDiseases):

	#Generate a unique set of labels
	labels = [each for title in extracted_labels.keys() for each in extracted_labels[title]]
	unique_labels = set(labels)
    
    #Find labels, their parent and write it to a file
	with open("task4.txt","w") as filewrite:
		for label in unique_labels:
			child_doid_obj = infoOfDiseases[map_labelToLocation[label]]
			child_label = child_doid_obj.label[0]
			#print(child_label)
			if child_label == "disease":
				continue
            #find parent
			parent_doid = infoOfDiseases[map_labelToLocation[label]].is_a[0]
			index_parent_doid_obj = infoOfDiseases.index(parent_doid)
			parent_doid_obj = infoOfDiseases[index_parent_doid_obj]
			parent_label = parent_doid_obj.label[0]


			filewrite.write(f"{child_label} <{str(child_doid_obj)}> is_a {parent_label} <{parent_doid}>\n")

	print(f"*********** Task 4 file entity relationship file created ***********\n")

task4_extractRelationship(extracted_labels,map_labelToLocation,infoOfDiseases)
