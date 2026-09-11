<script>
	export default {
		onLaunch: function() {}
	}
</script>

<style>
	/* 全局医疗健康主题：页面保持轻盈、清晰和一致的层次 */
	page {
		background: #F8FAFC;
		color: #1E293B;
		font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
		font-size: 28rpx;
		-webkit-font-smoothing: antialiased;
	}

	button::after { border: none; }
	button { box-sizing: border-box; }

	.tab-item,
	.menu-item,
	.quick-card,
	.shortcut-card,
	.entry-card,
	button {
		transition: transform 120ms ease-out, opacity 120ms ease-out;
	}

	.tab-item:active,
	.menu-item:active,
	.quick-card:active,
	.shortcut-card:active,
	.entry-card:active,
	button:active {
		transform: scale(0.97);
		opacity: 0.82;
	}
</style>
