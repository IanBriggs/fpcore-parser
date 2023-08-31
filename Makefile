# Default / Help message
.PHONY: help
help:
	@echo "Make targets are:"
	@echo "  nightly:   run the nightly test script"
	@echo "  clean:     remove generated files"
	@echo "  distclean: clean and remove nightly data"

# Run nightly
.PHONY: nightly
nightly: scripts/nightly.sh
	$<

# Normal clean
.PHONY: clean
clean:
	find . -type d -name "__pycache__" -exec ${RM} -r {} +

# Clean everything
.PHONY: distclean
distclean: clean
	$(RM) -r nightlies
