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
# B  Organisms (Exclusion Candidate)
# H Disciplines and Occupations (Reinclusion Candidate)
# I Anthropology, Education, Sociology
# K Humanities
# V Publication Types
# Z Geographic Locations

included_branches = {
    "A",
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
    if term.attrib.get("ConceptPreferredTermYN") == "N":
      s = term.findtext("String", default="").strip()
      if s and s.lower() not in seen:
        entry_terms.append(s)
        seen.add(s.lower())
      if len(entry_terms) >= max_entry_terms:
        break

  return {
      "id": uid,
      "name": name,
      "scope": scope,
      "tree_numbers": tree_numbers,
      "entry_terms": entry_terms,
  }

# parse the full NLM MeSH descriptor XML and return filtered descriptors
def parse_mesh_xml(xml_path: str) -> list[dict]:
  log.info(f"Parsing MeSH XML from: {xml_path}")
  tree = ET.parse(xml_path)
  root = tree.getroot()

  records = root.findall("DescriptorRecord")
  log.info(f"Total descriptor records found: {len(records)}")

  descriptors = []
  skipped = 0
  for record in records:
    parsed = parse_descriptor(record)
    if parsed:
      descriptors.append(parsed)
    else:
      skipped += 1

  log.info(f"Descriptors included: {len(descriptors)}")
  log.info(f"Descriptors skipped: {skipped}")
  return descriptors

# ---
# Output
# ---

def write_output(descriptors: list[dict], output_path: str) -> None:
  out = Path(output_path)
  out.parent.mkdir(parents=True, exist_ok=True)
  with open(out, "w", encoding="utf-8") as f:
    json.dump(descriptors, f, indent=2, ensure_ascii=False)
  log.info(f"Wrote {len(descriptors)} descriptors to {output_path}")

# ---
# Summary Report
# ---

# Print a breakdown of included descriptors by top-level branch
def print_summary(descriptors: list[dict]) -> None:
  from collections import Counter
  branch_counts = Counter()
  for d in descriptors:
    for tn in d["tree_numbers"]:
      branch_counts[tn[0]] += 1
      break

  print("\n--- Branch Summary ---")
  for branch in sorted(branch_counts):
    print(f" {branch}: {branch_counts[branch]} descriptors")
  print(f" TOTAL: {len(descriptors)} descriptors")

  no_scope = sum(1 for d in descriptors if not d["scope"])
  no_entry = sum(1 for d in descriptors if not d["entry_terms"])
  print(f"\n Descriptors with no scope note: {no_scope}")
  print(f" Descriptors with no entry terms: {no_entry}")
  print()

# ---
# Command Line Interface
# ---

def main():
  parser = argparse.ArgumentParser(description="Build SAMA MeSH descriptor bank from NLM XML.")
  parser.add_argument(
    "--xml",
    required=True,
    help="Path to NLM MeSH descriptor XML file (e.g. desc2025.xml)"
  )
  parser.add_argument(
    "--output",
    default="data/mesh/descriptors.json",
    help="Output path for descriptors JSON (default: data/mesh/descriptors.json)"
  )
  args = parser.parse_args()

  descriptors = parse_mesh_xml(args.xml)
  print_summary(descriptors)
  write_output(descriptors, args.output)

if __name__ == "__main__":
  main()


  
  
  


