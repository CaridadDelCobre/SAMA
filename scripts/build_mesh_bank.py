"""
Parses the NLM MeSH descriptor XML file, filters descriptors to 
SAMA-relevant tree branches, enriches each descriptor with entry term 
synonyms, and writes the result to data/mesh/descriptors.json

Usage:
  python scripts/build_mesh_bank.py --xml path/to/desc2025.xml --output data/mesh/descriptors.json

Download the MeSH descriptor XML from:
  https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/xmlmesh

"""
import xml.etree.ElementTree as ET
import json
import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format = "%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# ---
# Tree Branch Configuration
# ---

# A  Anatomy
# B  Organisms (Exclusion Candidate)
# C  Diseases
# D  Chemicals and Drugs
# E  Analytical, Diagnostic and Therapeutic Techniques and Equipment
# F  Psychiatry and Psychology
# G  Biological Sciences
# J  Technology, Industry, Agriculture
# L  Information Science
# M  Named Groups
#
# Excluded by default:
# H Disciplines and Occupations (Reinclusion Candidate)
# I Anthropology, Education, Sociology
# K Humanities
# V Publication Types
# Z Geographic Locations

included_branches = {
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "J",
    "L",
    "M",
    "N",
}

# Descriptors to exclude by name regardless of branch

excluded_names = {
    "Humans",
    "Animals",
    "Male",
    "Female",
    "Adult",
    "Aged",
    "Middle Aged",
    "Young Adult",
    "Adolescent",
    "Child",
    "Infant",
    "Models, Theoretical",
    "Models, Biological",
    "ROC Curve",
    "Sensitivity and Specificity",
    "Reproducibility of Results",
    "Treatment Outcome",
    "Prognosis",
    "Risk Factors",
    "Retrospective Studies",
    "Prospective Studies",
    "Follow-Up Studies",
    "Case-Control Studies",
    "Cohort Studies",
    "Cross-Sectional Studies",
    "Surveys and Questionnaires",
}

# maximum number of synonyms per term (entry terms in xml file)
max_entry_terms = 10

# ---
# Parsing
# ---

# return TRUE if any of the descriptor's tree numbers fall in an included branch
def is_included(tree_numbers: list[str]) -> bool:
  for tn in tree_numbers:
    prefix = tn.split(".")[0][0]
    if prefix in included_branches:
      return True
  return False

def parse_descriptor(record: ET.Element) -> dict | None:
  uid = record.findtext("DescriptorUI", default="").strip()
  name = record.findtext("DescriptorName/String", default="").strip()

  if not uid or not name:
    return None
    
  tree_numbers = [
    tn.text.strip()
    for tn in record.findall("TreeNumberList/TreeNumber")
    if tn.text
  ]

# Conditional that there are no matches in predefined list
if not is_included(tree_numbers):
  return None 

scope = ""
for concept in record.findall("ConceptList/Concept"):
  if concept.attrib.get("PreferredConceptYN") == "Y":
    scope_el = concept.find("ScopeNote")
    if scope_el is not None and scope_el.text:
      scope = scope_el.text.strip()
    break

entry_terms = []
seen = {name.lower()} # avoid duplicating the preferred name
  for term in record.findall("ConceptList/Concept/TermList/Term"):
    if term.attrib


