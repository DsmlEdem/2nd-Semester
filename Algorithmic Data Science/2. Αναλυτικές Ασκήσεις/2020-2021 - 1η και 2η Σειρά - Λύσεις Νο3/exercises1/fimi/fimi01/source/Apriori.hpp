/***************************************************************************
                          apriori.h  -  description
                             -------------------
    begin                : cs dec 26 2002
    copyright            : (C) 2002 by Ferenc Bodon
    email                : bodon@mit.bme.hu
 ***************************************************************************/

#ifndef APRIORI_H
#define APRIORI_H

#include "Trie.hpp"
#include "Trie_hash.hpp"
#include <map>


/**
  *@author Bodon Ferenc
  */

/// This struct is responsible for comparing two itemsets
struct itemsetLess: public binary_function<const vector<itemtype>& , const vector<itemtype>&, bool>
{
   bool operator()( const vector<itemtype>& basket_1, const vector<itemtype>& basket_2 ) const
   {
      itemtype item_index_1 = 0,
               item_index_2 = 0;
      while( item_index_1<basket_1.size() && item_index_2 < basket_2.size() )
         if( basket_1[item_index_1] < basket_2[item_index_2] ) return true;
         else if( basket_1[item_index_1] > basket_2[item_index_2] ) return false;
         else
         {
            item_index_1++;
            item_index_2++;
         }
      if( item_index_1 == basket_1.size() && item_index_2 < basket_2.size() ) return true;
      else return false;
   }
};

/** This class implements the APRIORI algirithm.

<p>
APRIORI is a levelwise algorithm.
It scans the transaction database several times.
After the first scan the frequent 1-itemsets are found, and in general after the <em>k<sup>th</sup></em> scan the frequent <em>k</em>-itemsets are extracted.
The method does not determine the support of every possible itemset.
In an attempt to narrow the domain to be searched, before every pass it generates <em>candidate</em> itemsets.
An itemset becomes a candidate if every subset of it is frequent.
Obviously every frequent itemset needs to be candidate too, hence only the support of candidates is calculated.
Frequent <em>k</em>-itemsets generate the candidate <em>k+1</em>-itemsets after the \f$k^{th}\f$ scan.
</p>

<p>
After all the candidate <em>k+1</em>-itemsets have been generated, a new scan of the transactions is effected and the precise support of the candidates is determined.
The candidates with low support are thrown away.
The algorithm ends when no candidates can be generated.
</p>

<p>
The intuition behind candidate generation is based on the following simple fact:<br>
<div align="center"><em>Every subset of a frequent itemset is frequent.</em></div><br>
This is immediate, because if a transaction <em>t</em> supports an itemset <em>X</em>, then <em>t</em> supports every subset \f$Y\subseteq X\f$.
</p>

<p>
Using the fact indirectly, we infer, that if an itemset has a subset that is infrequent, then it cannot be frequent.
So in the algorithm APRIORI only those itemsets will be candidates whose every subset is frequent.
The frequent <em>k</em>-itemsets are available when we attempt to generate candidate <em>k+1</em>-itemsets.
The algorithm seeks candidate <em>k+1</em>-itemsets among the sets which are unions of two frequent <em>k</em>-itemsets.
After forming the union we need to verify that all of its subsets are frequent, otherwise it should not be a candidate.
To this end, it is clearly enough to check if all the <em>k</em>-subsets of <em>X</em> are frequent.
</p>

<p>
Next the supports of the candidates are calculated.
This is done by reading transactions one by one.
For each transaction <em>t</em> the algorithm decides which candidates are supported by <em>t</em>.
To solve this task efficiently APRIORI uses a hash-tree.
However in this implementation a trie (prefix-tree) is applied.
Tries have many advantages over hash-trees.
<ol>
  <li> It is faster </li>
  <li> It needs no parameters (main drawback of a hash-tree is that its performance is very sensitive to the parameteres) </li>
  <li> The candidate generation is very simple. </li>
</ol>
</p>
*/

class Apriori {
public:
   Apriori( const bool& store_input, const int& trie_type=1, const int& child_threshold = 5 );

   /// This procedure implements the APRIORI algorithm
   void APRIORI_alg( ofstream& outcomefile, const char* basket_filename, const double& min_supp, const double& min_conf );

private:

   /// Reads in one transaction from the datafile.
   void read_in_a_line( FILE* filepoint );
   /// Determines the support of the candidates of the given size
   void support( FILE* filepoint, const itemtype& candidate_size );

   Trie*                                             trie;
   vector<itemtype>                                  basket;
   unsigned long                                     basket_number;
   map<vector<itemtype>, unsigned long, itemsetLess> reduced_baskets;
   bool                                              store_input;
};

#endif
