<script>
	export default {
		onLaunch: function() {}
	}
</script>

<style>
	/*每个页面公共css */
	page {
		background: #F8FAFC;
		color: #1E293B;
		font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
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
