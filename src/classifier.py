import os
from tflite_support.task import core
from tflite_support.task import text
import json
import re
import struct
import pandas as pd
from typing import List, Dict

class TopicsClassifier:
    def __init__(self) -> None:
        self.model_version = "chrome5"
        self.load_config()
        self.load_taxonomy()
        self.load_model()
        self.load_override_list()

    def load_config(self):
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                 self.model_version, "config.json")
        with open(config_path, "r") as f:
            self.config = json.load(f)

    def load_taxonomy(self):
        taxonomy_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                   self.model_version,
                                   self.config["taxonomy_filename"])
        taxonomy_df = pd.read_csv(taxonomy_path, sep="\t")
        self.taxonomy = taxonomy_df.set_index(self.config["taxonomy_id_column"])[self.config["taxonomy_name_column"]].to_dict()
        self.taxonomy[self.config["unknown_topic_id"]] = self.config["unknown_topic_name"]

    def get_all_topics(self) -> List[Dict[str, any]]:
        """Get all available topics from the taxonomy."""
        return [{"id": topic_id, "name": name} 
                for topic_id, name in self.taxonomy.items()
                if topic_id != self.config["unknown_topic_id"]]

    def load_model(self):
        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                self.model_version,
                                self.config["model_filename"])
        base_options = core.BaseOptions(file_name=model_path)
        text_classifier_options = text.BertNLClassifierOptions(base_options=base_options)
        self.model = text.BertNLClassifier.create_from_options(text_classifier_options)

    def load_override_list(self):
        override_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                   self.model_version,
                                   self.config["override_list_filename"])
        override_df = pd.read_csv(override_path, sep="\t")
        self.override_list = {}
        for _, row in override_df.iterrows():
            topics = row[self.config["override_list_topics_column"]]
            if pd.isna(topics):
                self.override_list[row[self.config["override_list_input_column"]]] = []
            else:
                self.override_list[row[self.config["override_list_input_column"]]] = [
                    int(topic) for topic in str(topics).split(",")
                ]

    def clean_input(self, input: str) -> str:
        cleaned_input = re.sub(self.config["meaningless_prefix_regex"], "", input.lower())
        replace_chars = ["-", "_", ".", "+"]
        for rc in replace_chars:
            cleaned_input = cleaned_input.replace(rc, " ")
        return cleaned_input

    def model_inference(self, input: str):
        cleaned_input = self.clean_input(input)
        result = self.model.classify(cleaned_input)
        return result.classifications[0].categories

    def topics_api_filtering(self, categories) -> List[Dict[str, str]]:
        # Order according to classification score, keep max ones only
        topics = sorted(
            categories,
            key=lambda x: x.score,
            reverse=True,
        )[:self.config["max_categories"]]

        # Sum scores, check if unknown topic in there
        top_sum = sum(t.score for t in topics)
        unknown_score = next(
            (t.score for t in topics if int(t.category_name) == self.config["unknown_topic_id"]),
            None
        )

        # If unknown topic there and too important, output unknown
        if (unknown_score and unknown_score / top_sum >
            struct.unpack("!f", bytes.fromhex(self.config["min_none_weight"]))[0]):
            return [{"id": self.config["unknown_topic_id"],
                    "name": self.taxonomy[self.config["unknown_topic_id"]]}]

        # Go through inferred topics, normalize scores, and check
        filtered_topics = []
        for t in topics:
            topic_id = int(t.category_name)
            if (topic_id != self.config["unknown_topic_id"] and
                t.score >= struct.unpack("!f", bytes.fromhex(self.config["min_category_weight"]))[0] and
                t.score / top_sum >= struct.unpack("!f", bytes.fromhex(self.config["min_normalized_weight_within_top_n"]))[0]):
                filtered_topics.append({
                    "id": topic_id,
                    "name": self.taxonomy[topic_id]
                })

        # Return unknown if no topic passes the filtering
        return filtered_topics or [{"id": self.config["unknown_topic_id"],
                                  "name": self.taxonomy[self.config["unknown_topic_id"]]}]

    def extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        # Remove protocol
        domain = re.sub(r'^https?://', '', url)
        # Remove path, query parameters, and fragment
        domain = domain.split('/')[0]
        # Remove port number if present
        domain = domain.split(':')[0]
        return domain

    def classify_domain(self, domain: str) -> List[Dict[str, str]]:
        # Clean domain if it's actually a URL
        if '://' in domain or '/' in domain:
            domain = self.extract_domain(domain)
            
        cleaned_domain = self.clean_input(domain)
        
        # Check override list first
        if cleaned_domain in self.override_list:
            topics = self.override_list[cleaned_domain]
            if not topics:
                return [{"id": self.config["unknown_topic_id"],
                        "name": self.taxonomy[self.config["unknown_topic_id"]]}]
            return [{"id": topic_id, "name": self.taxonomy[topic_id]}
                    for topic_id in topics]

        # Model inference and filtering
        categories = self.model_inference(domain)
        return self.topics_api_filtering(categories)