/***************************************************************************
                          trie.h  -  description
                             -------------------
    begin                : cs dec 26 2002
    copyright            : (C) 2002 by Ferenc Bodon
    email                : bodon@mit.bme.hu
 ***************************************************************************/

#ifndef TRIE_H
#define TRIE_H

/**
  *@author Ferenc Bodon
  */

typedef unsigned long itemtype;
//typedef unsigned short itemtype;

#include <fstream>
#include <iostream>
#include <set>
#include <vector>
#include <cstdio>
using namespace std;

/** Trie (or prefix-tree) is a tree-based datastructure.

   Trie is a rooted directed tree. The root is defined to be at depth 0, and a node at depth <em>d</em> can point to nodes at depth <em>d+1</em>.
   A pointer is also called edge or link, which is labeled by an item.
   If node <em>u</em> points to node <em>v</em>, then we call <em>u</em> the parent of <em>v</em>, and <em>v</em> is a child node of <em>u</em>.

*/

class Trie
{

public:

   Trie();

   /// Generates candidates.
   void candidate_generation( const itemtype& frequent_size );

   /// Increases the counter of those candidates that are contained by the given basket.
   void find_candidate( const vector<itemtype>& basket, const itemtype candidate_size, const unsigned long counter=1 );

   /// Deletes unfrequent itemsets.
   void delete_infrequent( const unsigned long min_occurrence );

   /// Generates association rules
   void association( ofstream& outcomefile, const double min_conf ) const;

   /// Recodes the basket so that each item is substituted by its s frequency order (inv_orderarray[]).
   void basket_recode( vector<itemtype>& basket ) const;

   /// Returns the number of nodes in the trie
   unsigned long node_number() const;

   /// Displays the memory need of the trie
   virtual void statistics() const;

   /// Writes the content (frequent itemsets) to the file
   void write_content_to_file( ofstream& outcomefile ) const;

   /// Displays the trie
   virtual void show_content() const;

   virtual ~Trie();

protected:

   /// Sets the maximal path value.
   virtual void max_path_set( const unsigned long state_index );

   /// Deletes the edge that goes to a given state.
   virtual void delete_edge( const unsigned long from_state, const unsigned long to_state );

   /// Adds an empty state to the trie
   virtual void add_empty_state( const unsigned long from_state, const itemtype item, const unsigned long counter=0 );

   /// It decides whether the given itemset is included in the trie or not.
   virtual unsigned long is_included( const set<itemtype>& an_itemset ) const;

   /// Decides if all subset of of an itemset is contained in the trie
   bool is_all_subset_frequent( const set<itemtype>& maybe_candidate ) const;

   /// Generates candidate of size two
   void candidate_generation_two();

   /// Generates candidate of size more than two
   virtual void candidate_generation_assist( unsigned long actual_state, const itemtype frequent_size,
                                             const itemtype actual_sizet, set<itemtype>& maybe_candidate );

   /// Increases the counter for those items that are in the given basket.
   void find_candidate_one( const vector<itemtype>& basket );

   /// Increases the counter for those itempairs that are in the given basket.
   void find_candidate_two( const vector<itemtype>& basket, const unsigned long counter=1 );

   /// Increases the counter for those itemsets that is contained by the given basket.
   virtual void find_candidate_more( const vector<itemtype>& basket, const itemtype candidate_size,
                                     vector<itemtype>::const_iterator it_basket, const unsigned long actual_state,
                                     const itemtype actual_size, const unsigned long counter=1 );

   /// Deletes the nodes that represent infrequent itemsets of size 1.
   virtual void delete_infrequent_one( const unsigned long min_occurrence );

   /// Deletes the nodes that represent infrequent itemsets of size 2.
   virtual void delete_infrequent_two( const unsigned long min_occurrence );

   //! Deletes the nodes that represent infrequent itemsets.
   virtual void delete_infrequent_more( const unsigned long min_occurrence );

   void assoc_rule_find( ofstream& outcomefile, const double min_conf, set<itemtype>& condition_part,
                         set<itemtype>& consequence_part, const unsigned long union_support) const;

   virtual void assoc_rule_assist( ofstream& outcomefile, const double min_conf,unsigned long actual_state,
                                   set<itemtype>& consequence_part) const;

   //! Writes out the content of the trie (frequent itemset and counters).
   virtual void write_content_to_file_assist( ofstream& outcomefile, const unsigned long actual_state, const itemtype item_size,
                                              const itemtype actual_size,set<itemtype>& frequent_itemset) const;
private:
   // No private methods

public:
   // No public members

protected:
   /** itemarray stores the label of the edges.
     *
     * itemarray[i] belongs to the i<sup>th</sup> node.
     * itemarray[i][j] stores the label of the j<sup>th</sup> edge (of the i<sup>th</sup> node).
     * A label is a positive integer number (the code of an item).
     */
   vector< vector<itemtype> > itemarray;

   /**  stetearray stores the end node of the edges.
     *
     * statearray[i] belongs to the i<sup>th</sup> node.
     * statearray[i][j] stores the end node of the j<sup>th</sup> edge (of the i<sup>th</sup> node).
     */
   vector< vector<unsigned long> > statearray;

   /**  countervector stores the occurences of the itemsets
     *
     * countervector[i] stores the occurence of the itemset represented by the i<sup>th</sup> node.
     */
    vector<unsigned long> countervector;

    vector<unsigned long> parent;

   /**  temp_counter_array stores the occurences of the itempairs
     *
     * countervector[i][j] stores the occurence of the itempair (orderarray[i],orderarray[j]).
     */
   vector< vector<unsigned long> > temp_counter_array;

   /**  maxpath stores the legth of the longest paths.
     *
     * maxpath[i] stores the legth of the longest path starting from the i<sup>th</sup> node.
     */
  vector<itemtype> maxpath;

  /**  The frequency order of the items
    *
    * orderarray[1] is the most frequent item, orderarray[2] is the second most frequent...
    */
  vector<itemtype> orderarray;

  ///  inverse of orderarray: orderarray[inv_orderarray[i]]=i
  vector<itemtype> inv_orderarray;


};

#endif
