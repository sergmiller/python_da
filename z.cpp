#include <iostream>
#include <fstream>
#include <vector>
#include <stack>
#include <algorithm>
#include <queue>
#include <string>
#include <cmath>
#include <map>
#include <set>
#include <cassert>
#define MOD (ll)1e9 + 7
#define eps (ld)1e-30
#define pb push_back
#define mp make_pair
#define ft first
#define sd second
#define sz(a) a.size()
#define loop(i, n) for(long long (i) = 0; (i) < (n) ; ++ (i))
#define loopn()
#define pii pair<int,int>
#define pll pair<long long,long long>
#define pld pair<long double,long double>
#define vii vector<int>
#define vll vector<long long>  
typedef long long ll;
typedef long double ld;
 
using namespace std;
 

/*@Sergey_Miller*/

ll n;
ll a[301];
ll dp[301][301][2];
ll fl[301][301][2];

ll get(ll l, ll r, ll ind) {
    if(l == r)
        return 0;
    if(ind != -1) {
        if(fl[l][r][ind]) {
            return dp[l][r][ind];
        } else {
            fl[l][r][ind] = 1;
        }
    }

    ll best = 0;
    ll bnd;
    if(!ind)
        bnd = a[l-1];
    else
        bnd = a[r];
    for(ll i = l; i < r; ++i) {
        if(ind == -1 || a[i] < bnd) {
            ll lh = get(l,i,1);
            ll rh = get(i+1,r,0);
            best = max(best, max(lh, rh) + 1);
        }
    }
    return dp[l][r][ind] = best;
}

void solve() {
    cin >> n;
    loop(i,n)
        cin >> a[i];
    cout << get(0,n,-1);
}


int main () {
    ios::sync_with_stdio(false);
    // freopen("out", "r", stdin);
    // freopen("output.txt", "w", stdout);

    solve();
    return 0;


}