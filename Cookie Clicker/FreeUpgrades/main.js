Game.registerMod("free upgrades", {
	init: function() {
		// 1. Bypass fungsi pengurangan cookies (Game.Spend)
		// Ini menjamin saldo cookies TIDAK AKAN PERNAH BERKURANG saat membeli apapun
		Game.Spend = function(howmuch) {
			// Do nothing - belanja gratis!
		};

		// 2. Gratiskan semua Upgrade (icon kecil di atas Store)
		Game.Upgrade.prototype.getPrice = function() {
			return 0;
		};
		Game.Upgrade.prototype.canBuy = function() {
			return true;
		};

		// 3. Gratiskan semua Bangunan / Buildings (Cursor, Grandma, Farm, Mine, dll.)
		if (Game.Objects) {
			for (var i in Game.Objects) {
				Game.Objects[i].getPrice = function() {
					return 0;
				};
			}
		}

		// Daftarkan hook logic agar bangunan baru atau kalkulasi ulang tetap 0
		Game.registerHook('logic', function() {
			for (var i in Game.Objects) {
				if (Game.Objects[i].getPrice() !== 0) {
					Game.Objects[i].getPrice = function() { return 0; };
				}
			}
		});

		// Refresh tampilan toko (Store)
		Game.upgradesToRebuild = 1;
		Game.recalculateGains = 1;

		// Notifikasi in-game
		Game.Notify('FREE UPGRADE AKTIF!', 'Cookies tidak akan berkurang saat membeli upgrade maupun bangunan.', [16, 5], 6);
	},
	save: function() {
		return '';
	},
	load: function(str) {}
});
