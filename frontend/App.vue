<script>
	export default {
		onLaunch: function() {}
	}
</script>

<style>
	/*每个页面公共css */
	page {
		background: #F4F7F5;
		color: #17231F;
		font-family: "Avenir Next", "PingFang SC", "Microsoft YaHei", sans-serif;
		--status-bar-height: 44px;
	}

	button::after {
		border: none;
	}

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
		transform: scale(0.96);
		opacity: 0.82;
	}

</style>
