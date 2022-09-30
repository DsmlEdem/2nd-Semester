/** \mainpage An efficient implemenation of APRIORI algorithm

This program is a very efficient implementation of APRIORI algorithm proposed by Rakesh Agrawal and Ramakrishnan Srikant.
APRIORI is the most basic and well-known algorithm to find frequent itemsets in a transactional database.

<h2>Frequent Itemset Mining problem</h2>
A <i>transactional database</i> consists of sequence of transaction: \f$T=\langle t_1,\ldots ,t_n\rangle \f$.
A transaction is a set of items (\f$t_i\in I\f$).
Transactions are often called <i>baskets</i>, referring to the primary application domain (i.e. market-basket analysis).
A set of items is often called <i>itemset</i> by the data mining community.
The <i>(absolute) support</i> or the <em>occurrence</em> of \f$X\f$ (denoted by \f$supp(X)\f$) is the number of transactions that are supersets of \f$X\f$ (i.e. that <em>contain</em> \f$X\f$).
The <em>realtive support</em> is the absolute support divided by the number of transactions (i.e. <i>n</i>).
An itemset is <i>frequent</i> if its support is greater or equal than a threshold value.

<p>In the frequent itemset mining problem a transaction database and a relative support threshold (traditionally denoted by <i>min_supp</i>) is given and we have to find all frequent itemsets.
</p>

<h2>Association Rule Mining problem</h2>
This program is also capable of mining association rules.
An association rule is like an implication: \f$X\to Y \f$ means that if itemset <em>X</em> occurs in a transaction, than itemset <em>Y</em> also occurs with high probability.
This probability is given by the <em>confidence</em> of the rule.
It is like an approxiamtion of <em>p(Y|X)</em>, it is the number of transactions that contain both <em>X</em> and <em>Y</em> divided by the number of transaction that contain <em>X</em>, thus \f$conf(X\to Y)=\frac{supp(X\cup Y)}{supp(X)}\f$.
The <em>relative support</em> of the association rule \f$X\to Y \f$ is the support of itemset \f$X \cup Y \f$.
The lift of \f$X\to Y \f$ tries to capture the independence of the antecedent and the consequent of the rule: \f$lift(X\to Y)=\frac{supp(X\cup Y)}{supp(X)supp(Y)}\f$
An association rule is <em>valid</em> if its confidence, support and lift are greater than or equal than corresponding threshold values.

<p>In the association rule mining problem a transaction database and a relative support threshold (traditionally denoted by <i>min_supp</i>), a confidence threshold (traditionally denoted by <i>min_conf</i>), and a lift threshold is given and we have to find all valid association rules.
</p>
 */

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif

#include <fstream>
#include <unistd.h>
#include <getopt.h>
#include "Apriori.hpp"
using namespace std;

/// This procedure displays the usage of the program.

void usage()
{
   cerr << "\nUsage: apriori [options] basketfile outcomefile min_supp [min_conf]\n";
   cerr << "\n basketfile\t    file, that contains the baskets of itemcodes";
   cerr << "\n outcomefile\t    file to write the outcome";
   cerr << "\n min_supp\t    support threshold";
   cerr << "\n min_conf\t    confidence threshold";

   cerr << "\n\nBasic options:";
   cerr << "\n -h| --help\t    Gives this help display.";
   cerr << "\n --hash <num>       use hash techniques in the trie.";
   cerr << "\n\t\t    Trie with hash technique is faster but needs more memory!";
   cerr << "\n\t\t    Hash technique is applied at nodes,";
   cerr << "\n\t\t    that have children more than num,";
   cerr << "\n\t\t    type --trie_hash 0 for default (5) child threshold,";
   cerr << "\n --no_store_input\n  -s\t\t    Do not store filtered basket (i.e frequent items";
   cerr << "\n\t\t    in the basket) in memory. This decreases memory need,";
   cerr << "\n\t\t    but slows down the algorithm!";

   cerr << "\n\nFile formats:";
   cerr << "\n\nThe basket file is a plan text file. Each row represents a basket.";
   cerr << "A basket is a set of items seperated by a nonnumeric character (for example white space, comma, colon, etc.).";
   cerr << "An item is represented by its code which is an integer number greater than or equal to 0.";
   cerr << "\n\nHave a succesful mining ;-)";
   cerr << "\n\n\n\t\t\t\t\tFerenc Bodon\n\n";
}

int main( int argc, char *argv[] )
{
   double min_supp,min_conf;
   int trie_type=1, child_threshold=30, optch, cmdindex=0;
   char stropts[]="ht:s";
   bool store_input=true;
   struct option lopts[]=
   {
      {"help",0,0,'h'},
      {"store_input",0,0,'s'},
      {"hash",1,0,'t'},
      {0,0,0,0}
   };

  while ( (optch = getopt_long(argc,argv,stropts,lopts,&cmdindex))!=EOF )
     switch ( optch )
     {
        case 'h' : usage();exit(1);
        case 's' : store_input = false; break;
        case 't' : trie_type = 2;
                child_threshold=atoi(optarg);
                if (child_threshold<1) child_threshold = 30;
                break;

        default:   cerr<<"\nType --help for help.\n"; exit(1);
     }
  if ( argc < optind+3 )
  {
     cerr<<"\nThere are 3 mandatory arguments!";
     cerr<<"\nType --help for help.\n";
     exit(1);
  }

   cout << "\n********************************************************************";
   cout << "\n***                                                              ***";
   cout << "\n***             Trie/Trie-hash based APRIORI algorithm           ***";
   cout << "\n***                       version: 1.4.03                        ***";
   cout << "\n***                                                              ***";
   cout << "\n***       Implemented by: Ferenc Bodon (bodon@mit.bme.hu)        ***";
   cout << "\n***                                                              ***";
   cout << "\n********************************************************************\n\n";

   min_supp = atof(argv[optind+2]);
   if ( min_supp <= 0 || min_supp > 1 )
   {
      cout<<"\nError!\n min_supp should be in the interval (0,1].\n";
      cout.flush();
      exit(1);
   }
   if ( argc == optind+3 ) min_conf = 0;
   else
   {
      min_conf = atof(argv[optind+3]);
      if ( min_conf <= 0 || min_conf > 1 )
      {
         cout << "\nError!\n min_conf should be in the interval (0,1].\n";
         cout.flush();
         exit(1);
      }
   }
   ofstream outcomefile(argv[optind+1]);
   if ( !outcomefile ) {cerr << "\nThe outcomefile can not be written!"<< flush; exit(1);}

   Apriori apriori( store_input, trie_type, child_threshold );
   apriori.APRIORI_alg( outcomefile, argv[optind], min_supp, min_conf );
   outcomefile.close();
   return 0;
}
