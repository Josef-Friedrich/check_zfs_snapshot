wget_github = wget -O $(1) https://raw.githubusercontent.com/$(2) ; \
		chmod a+x $(1)

test:
	bats test

sync_dependencies:
	$(call wget_github,test/bash_unit,pgrange/bash_unit/master/bash_unit)
	$(call wget_github,test/test-helper.sh,JosefFriedrich-shell/test-helper/master/test-helper.sh)

.PHONY: test sync_dependencies
