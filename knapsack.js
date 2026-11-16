/*
  ====================================================================
  knapsack.js  -  0/1 KNAPSACK ke teeno algorithms
  ====================================================================

  PROBLEM (0/1 Knapsack):
    Hamare paas n items hain. Har item ka ek weight aur ek value hai.
    Bag ki capacity limited hai. Hum aise items chunna chahte hain ke
        1) un ka total weight  <=  capacity
        2) un ki total value   sabse ZYADA ho
    "0/1" ka matlab: har item ya poora lena hai (1) ya bilkul nahi (0).
    Item ka hissa nahi le sakte.

  CARGO PROJECT MEIN MAPPING:
    weights[i]  = i-th package ka weight
    values[i]   = i-th package ka profit
    capacity    = truck ki capacity

  Teeno functions ye input lete hain:
    weights  : array, har item ka weight   (whole numbers)
    values   : array, har item ki value
    capacity : bag ki capacity             (whole number)
  Aur ye return karte hain:
    best     : mil sakne wali sabse bari total value
    chosen   : chune gaye items ke indexes (0 se shuru)

  Teeno ka comparison:
    Algorithm      Time          Hamesha optimal?
    Brute Force    O(2^n)        Haan (lekin bohot slow)
    Greedy         O(n log n)    NAHI (0/1 mein galat ho sakta hai)
    DP             O(n * W)      Haan (aur tez)
  ====================================================================
*/


/* ====================================================================
   1) BRUTE FORCE  -  har mumkin combination try karo
   ====================================================================
   Idea:
     n items ke 2^n subsets hote hain (har item: lo ya na lo).
     Har subset ka weight check karo. Agar capacity mein fit ho aur
     pichle best se zyada value ho, to usay best bana lo.

   Trick (bitmask):
     0 se 2^n - 1 tak har number ek subset hai. Number ka i-th bit 1 ho
     to item i us subset mein hai.
     Misaal n=3:  mask = 5 = binary 101  ->  item 0 aur item 2.

   Time: O(2^n * n)  ->  n = 25 ke baad practically bohot slow.
   Faida: samajhna aasan, aur DP ka answer verify karne ke kaam aata hai.
*/
function bruteForce(weights, values, capacity) {
  const n = weights.length;
  let bestValue = 0;
  let bestItems = [];

  // mask har possible subset ko represent karta hai
  for (let mask = 0; mask < (1 << n); mask++) {
    let w = 0, v = 0;
    const items = [];

    // is subset ke items jodo
    for (let i = 0; i < n; i++) {
      if (mask & (1 << i)) {      // kya i-th bit 1 hai?
        w += weights[i];
        v += values[i];
        items.push(i);
      }
    }

    // valid subset (fit hota hai) aur ab tak ka best hai to save karo
    if (w <= capacity && v > bestValue) {
      bestValue = v;
      bestItems = items;
    }
  }
  return { best: bestValue, chosen: bestItems };
}


/* ====================================================================
   2) GREEDY  -  sabse acha "value / weight" ratio wala pehle uthao
   ====================================================================
   Idea:
     Har item ka ratio = value / weight nikalo (kitni value per kg).
     Ratio ke hisab se bare se chote ki taraf sort karo.
     Ek ek karke uthao, jo bag mein poora fit ho jaye.

   Time: O(n log n)  (zyada tar sorting ka time)

   WARNING - Ye 0/1 Knapsack mein hamesha OPTIMAL nahi hota!
     Misaal: capacity = 50
       A: weight 10, value 60   (ratio 6)
       B: weight 20, value 100  (ratio 5)
       C: weight 30, value 120  (ratio 4)
     Greedy: A, B uthata hai (weight 30, value 160); C ke liye jagah
             nahi bachti (20 kg free, C 30 kg ka hai).
     Best:   B + C = weight 50, value 220.
     Greedy 60 kam deta hai, kyunke ek achi item uthane se
     bag ki jagah zaya ho jati hai.
   (Fractional Knapsack mein item ka hissa le sakte hain, wahan
    isi tarah ka Greedy optimal hota hai.)
*/
function greedy01(weights, values, capacity) {
  // items ke indexes ko ratio ke hisab se sort karo (sabse bara ratio pehle)
  const order = weights.map((_, i) => i)
    .sort((a, b) => values[b] / weights[b] - values[a] / weights[a]);

  let totalW = 0, totalV = 0;
  const chosen = [];

  for (const i of order) {
    // sirf tab lo jab poora item bag mein fit ho jaye
    if (totalW + weights[i] <= capacity) {
      chosen.push(i);
      totalW += weights[i];
      totalV += values[i];
    }
    // warna is item ko chor do aur agle ko dekho (peeche nahi jate)
  }
  return { best: totalV, chosen: chosen.sort((a, b) => a - b) };
}


/* ====================================================================
   3) DYNAMIC PROGRAMMING  -  asli 0/1 Knapsack solution
   ====================================================================
   Idea:
     Bari problem ko chote hisson mein tor do aur har chote hisse ka
     answer ek table mein save karo, taake dobara na nikalna pare.

   TABLE ka matlab:
     dp[i][w] = sirf pehle i items ko dekh kar, w capacity wale bag mein
                mil sakne wali sabse bari value.
     Rows    : i = 0 .. n   (0 ka matlab abhi koi item nahi dekha)
     Columns : w = 0 .. capacity
     Final answer: dp[n][capacity]

   RECURRENCE (har cell par ek faisla):
     item i ka weight = weights[i-1], value = values[i-1]
     (i-1 isliye ke row 0 "koi item nahi" ke liye hai)

     Case 1: item w capacity mein fit hi nahi hota (weight > w)
             dp[i][w] = dp[i-1][w]               // lene ka option hi nahi

     Case 2: item fit hota hai, to do options mein se bara chuno:
             skip = dp[i-1][w]                   // item NA lo
             take = values[i-1]                  // item LO: uski value
                    + dp[i-1][w - weights[i-1]]  // + bachi capacity ka best
             dp[i][w] = max(skip, take)

   BASE CASE: dp[0][w] = 0 aur dp[i][0] = 0 (koi item ya capacity nahi
              to value 0). Table 0 se shuru hoti hai, isliye ye khud ho jata hai.

   MISAAL: weights = [1, 3, 4], values = [15, 20, 30], capacity = 4
            capacity ->  0   1   2   3   4
            i=0 (none)   0   0   0   0   0
            i=1 (1kg,15) 0  15  15  15  15
            i=2 (3kg,20) 0  15  15  20  35    <- w=4: lo = 20 + dp[1][1] = 35
            i=3 (4kg,30) 0  15  15  20  35    <- w=4: lo = 30 + 0 = 30 < 35, skip
     Answer = dp[3][4] = 35  (item 1 aur item 2).

   Time  : O(n * W)   (table ke har cell par ek baar kaam)
   Space : O(n * W)   (poori table save karte hain, backtracking ke liye)
   Note  : W input ki "value" par depend karta hai, size par nahi, isliye
           isay "pseudo-polynomial" kehte hain.
*/
function dp01(weights, values, capacity) {
  const n = weights.length;

  // ---- Step 1: table banao, (n+1) rows x (capacity+1) columns, sab 0 ----
  const dp = Array.from({ length: n + 1 }, () => new Array(capacity + 1).fill(0));

  // ---- Step 2: table fill karo (row by row, upar se neeche) ----
  for (let i = 1; i <= n; i++) {
    for (let w = 0; w <= capacity; w++) {
      if (weights[i - 1] > w) {
        // Case 1: item is capacity mein fit nahi hota
        dp[i][w] = dp[i - 1][w];
      } else {
        // Case 2: do options, jo behtar ho wo chuno
        const skip = dp[i - 1][w];                                       // item na lo
        const take = values[i - 1] + dp[i - 1][w - weights[i - 1]];      // item lo
        dp[i][w] = Math.max(skip, take);
      }
    }
  }

  // ---- Step 3: BACKTRACKING - pata lagao kaunse items liye gaye ----
  // Table ke aakhri cell dp[n][capacity] se shuru karo aur peeche jao.
  // Agar dp[i][w] upar wali row dp[i-1][w] se ALAG hai, to item i LIYA gaya
  // tha (kyunke item na lene par value upar wali row jaisi hi rehti).
  // Item lene ke baad capacity us ke weight jitni kam kar do.
  const chosen = [];
  const path = [];            // wo cells jahan item liya gaya (sirf highlight ke liye)
  let w = capacity;
  for (let i = n; i > 0; i--) {
    if (dp[i][w] !== dp[i - 1][w]) {   // value badli = item i liya gaya
      chosen.push(i - 1);              // item ka index (row i = item i-1)
      path.push([i, w]);
      w -= weights[i - 1];             // bachi hui capacity
    }
  }
  chosen.reverse();                    // peeche se aaye the, seedha karo

  return { best: dp[n][capacity], chosen, table: dp, path };
}


// Node mein test karne ke liye (browser mein ye line ignore ho jati hai)
if (typeof module !== "undefined") module.exports = { bruteForce, greedy01, dp01 };
