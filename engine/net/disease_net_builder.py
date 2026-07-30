#!/usr/bin/env python3
"""
INTERCEPTA Automated Disease Net Builder
=========================================
Given ANY disease name, builds a complete disease-specific net
by querying the Universal Net.

This is the core of our vision: "When a new disease emerges,
we do not build a new net. We query the existing net."

Author: Prasad Akula
Date: April 2026
"""
import pandas as pd
import json
import sys
import os

class DiseaseNetBuilder:
    def __init__(self, net_path='../results/mcrpc_unified_net.json',
                 assoc_path='../results/step8_gene_disease_associations.parquet',
                 names_path='../results/step8_disease_names.csv',
                 met_path='../results/step9_metabolome_gene_edges.csv',
                 immune_path='../results/step13_immune_expression.csv'):
        
        print("Loading Universal Net...")
        with open(net_path) as f:
            self.net = json.load(f)
        
        print("Loading disease associations...")
        self.assoc = pd.read_parquet(assoc_path)
        
        names = pd.read_csv(names_path)
        self.name_map = dict(zip(names['id'], names['name']))
        self.name_to_id = {}
        for did, name in self.name_map.items():
            self.name_to_id[name.lower()] = did
        
        print("Loading metabolome...")
        self.met = pd.read_csv(met_path)
        
        print("Loading immune map...")
        self.immune = pd.read_csv(immune_path, index_col=0)
        self.immune = self.immune[~self.immune.index.duplicated(keep='first')]
        
        print(f"Ready. {len(self.name_map)} diseases queryable.\n")
    
    def search_disease(self, query, top_n=10):
        """Search for diseases matching a query string."""
        query_lower = query.lower()
        matches = [(did, name) for did, name in self.name_map.items() 
                   if query_lower in name.lower()]
        matches.sort(key=lambda x: len(x[1]))  # shorter names first
        return matches[:top_n]
    
    def build_net(self, disease_id, min_score=0.1, max_genes=500):
        """Build a complete disease-specific net."""
        disease_name = self.name_map.get(disease_id, disease_id)
        print(f"Building net for: {disease_name} ({disease_id})")
        print("=" * 55)
        
        # Step 1: Get disease-associated genes
        disease_assoc = self.assoc[self.assoc['diseaseId'] == disease_id]
        disease_assoc = disease_assoc[disease_assoc['associationScore'] >= min_score]
        disease_assoc = disease_assoc.nlargest(max_genes, 'associationScore')
        
        genes = list(disease_assoc['gene'].unique())
        print(f"  Genes (score>{min_score}): {len(genes)}")
        
        if len(genes) == 0:
            print("  No genes found. Try lower min_score.")
            return None
        
        # Step 2: Extract all layers for these genes from universal net
        disease_net = {
            'disease': disease_name,
            'disease_id': disease_id,
            'n_genes': len(genes),
            'genes': {},
            'pathways': set(),
            'metabolites': set(),
            'drug_targets': [],
            'immune_relevant': [],
            'structures_available': [],
            'mutation_profile': {},
        }
        
        for gene in genes:
            score = float(disease_assoc[disease_assoc['gene']==gene]['associationScore'].max())
            gene_data = self.net['genes'].get(gene, {})
            
            entry = {
                'association_score': round(score, 4),
                'mutation_frequency': gene_data.get('mutation_frequency', 0),
            }
            
            # Drug correlations
            if gene_data.get('drug_correlations'):
                entry['n_drug_correlations'] = len(gene_data['drug_correlations'])
            
            # Interactions
            if gene_data.get('interactions'):
                entry['n_interactions'] = len(gene_data['interactions'])
            
            # Pathways
            if gene_data.get('pathways'):
                entry['pathways'] = gene_data['pathways']
                for p in gene_data['pathways']:
                    if isinstance(p, dict):
                        disease_net['pathways'].add(p.get('id', ''))
                    elif isinstance(p, str):
                        disease_net['pathways'].add(p)
            
            # Metabolites
            if gene_data.get('metabolites'):
                entry['metabolites'] = gene_data['metabolites']
                for m in gene_data['metabolites']:
                    disease_net['metabolites'].add(m)
            
            # Compounds (drug targets)
            if gene_data.get('compounds'):
                entry['n_compounds'] = len(gene_data['compounds']) if isinstance(gene_data['compounds'], list) else 1
                disease_net['drug_targets'].append(gene)
            
            # AlphaFold structure
            if gene_data.get('alphafold'):
                entry['alphafold'] = gene_data['alphafold']
                disease_net['structures_available'].append(gene)
            
            # Immune expression
            if gene in self.immune.index:
                row = self.immune.loc[gene]
                top_val = float(row.max())
                if top_val > 10:
                    entry['immune_top_cell'] = row.idxmax()
                    entry['immune_top_tpm'] = round(top_val, 1)
                    disease_net['immune_relevant'].append(gene)
            
            # Selectivity
            if gene_data.get('selectivity'):
                entry['selectivity'] = gene_data['selectivity']
            
            # CNA
            if gene_data.get('cna'):
                entry['cna'] = gene_data['cna']
            
            disease_net['genes'][gene] = entry
        
        # Convert sets to lists for JSON
        disease_net['pathways'] = list(disease_net['pathways'])
        disease_net['metabolites'] = list(disease_net['metabolites'])
        
        # Summary
        print(f"  Pathways involved: {len(disease_net['pathways'])}")
        print(f"  Metabolites linked: {len(disease_net['metabolites'])}")
        print(f"  Drug targets (with compounds): {len(disease_net['drug_targets'])}")
        print(f"  Immune-relevant genes: {len(disease_net['immune_relevant'])}")
        print(f"  Structures available: {len(disease_net['structures_available'])}")
        
        # Top 10 genes by association score
        top_genes = sorted(disease_net['genes'].items(), 
                          key=lambda x: -x[1]['association_score'])[:10]
        print(f"\n  Top 10 genes:")
        for gene, data in top_genes:
            extras = []
            if data.get('n_compounds'): extras.append(f"compounds={data['n_compounds']}")
            if data.get('metabolites'): extras.append(f"mets={len(data['metabolites'])}")
            if data.get('alphafold'): extras.append("AF=Y")
            extra_str = f" [{', '.join(extras)}]" if extras else ""
            print(f"    {gene:<12} score={data['association_score']:.3f}{extra_str}")
        
        return disease_net


if __name__ == '__main__':
    builder = DiseaseNetBuilder()
    
    # Demo: build nets for our expansion diseases
    diseases = [
        ('acute myeloid leukemia', 0.1),
        ('Alzheimer disease', 0.1),
        ('non-small cell lung carcinoma', 0.1),
        ('pancreatic ductal adenocarcinoma', 0.1),
        ('tuberculosis', 0.05),
    ]
    
    for query, min_score in diseases:
        matches = builder.search_disease(query)
        if matches:
            disease_id = matches[0][0]
            disease_name = matches[0][1]
            print(f"\n{'='*60}")
            net = builder.build_net(disease_id, min_score=min_score)
            if net:
                outfile = f"../results/disease_net_{query.replace(' ','_')[:30]}.json"
                with open(outfile, 'w') as f:
                    json.dump(net, f, indent=2)
                print(f"  Saved: {outfile}")
        else:
            print(f"  No match for: {query}")
