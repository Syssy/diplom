'use strict';

var enrichmentsModule = null;

// TODO - Get plural version of class labels
// from the API. See COD-96
function pluralize(word) {
	if (word[word.length-1] == 's') {
		return word + 'es';
	} else {
		return word + 's';
	}
}

/** Interface for requesting rendered images
 * from sections of a PDF for display in Enrichments
 * view elements.
 */
var PdfImageExtractor = function(enrichmentsModule) {
	this._imageRequests = [];

	var self = this;

	enrichmentsModule.imageExtracted.connect(function(requestId, image) {
		self._imageRequests.forEach(function(handler) {
			if (handler.requestId == requestId) {
				handler.callback(image);
			}
		});
	});

	this.requestImage = function(region, width, callback) {
		var requestId = enrichmentsModule.extractImage(region, width);
		self._imageRequests.push({
			requestId: requestId,
			callback: callback
		});
		return requestId > 0;
	};
};

/** Provides the UI for a native popup menu
 * attached to an element.
 */
var MenuButton = function(element) {
	this._menuIcon = element.children('.actions-arrow');
	this._menuButton = element.children('.actions-button');
	this._menuItems = [];

	this.addItem = function(menuItem) {
		this._menuItems.push(menuItem);
	}

	this.createMenu = function(menuItem) {
		if (this._menuItems.length > 0) {
			MendeleyUi.addMenu(this._menuButton, this._menuItems);
		} else {
			this._menuIcon.hide();
			this._menuButton.hide();
		}
	}
};

var OUTLINE_ENTRY = "Outline";
var TABLE_ENTRY = "Table";
var FIGURE_ENTRY = "Figure";
var SYSTEM_ENTRY = "SystemEntity";

/** Manages the view of entity annotations, grouped
 * into sections for tables, figures and other types
 * of annotation.
 *
 * The update() method handles refreshing the list
 * to display the current set of entity annotations
 * returned by enrichmentsModule.annotations
 */
var OutlineView = function(imageExtractor) {
	var self = this;
	this._imageExtractor = imageExtractor;
	this._selectedOutlineElements = [];

	self._addOutlineEntry = function(entry, index) {
		var typeString = 'item';
		entry.elementId = 'outline-' + index;
		if (entry.entityType == OUTLINE_ENTRY) {
			// these entries are displayed in the Contents tab
			// rather than the Enrichments tab
		} else if (entry.entityType == TABLE_ENTRY) {
			typeString = 'table';

			var tableTemplate = ich.table_template(entry, {});
			$('#section-tables-and-figures').append(tableTemplate);
		} else if (entry.entityType == FIGURE_ENTRY) {
			typeString = 'figure';

			var figureTemplate = ich.figure_template(entry, {});
			$('#section-tables-and-figures').append(figureTemplate);

			var jqImg = $('#' + entry.elementId + '-image');
			var imgElement = jqImg[0];
			var IMG_WIDTH = 300;
			jqImg.width(IMG_WIDTH);
			jqImg.height(entry.boundingBoxHeightForWidth(IMG_WIDTH));

			var renderStarted = this._imageExtractor.requestImage(entry.region, IMG_WIDTH, function(image) {
				// in older versions of QtWebKit, img.assignToHTMLImageElement()
				// assigns image to an <img> element.
				//
				// In newer versions this function was renamed to img.assignTo(),
				// but this crashes under Ubuntu 13.04 (x86) so use the less
				// efficient img.toDataUrl() instead.
				//
				// TODO - Debug issue with img.assignTo()
				if (typeof(image.assignToHTMLImageElement) !== 'undefined') {
					image.assignToHTMLImageElement(imgElement);
				} else {
					imgElement.src = image.toDataUrl();
				}
			});
			var imgUnavailableElement = $('#' + entry.elementId + ' .figure-image-unavailable');
			imgUnavailableElement.toggle(!renderStarted);
			jqImg.toggle(renderStarted);

		} else {
			console.log('Unknown entry type ' + entry.entityType);
		}

		var newElement = $('#' + entry.elementId);
		newElement.mousedown(function() {
			enrichmentsModule.select([entry.uuid]);
		});
		newElement.dblclick(function() {
			enrichmentsModule.showAnnotationsInViewer();
		});

		var tableDataElement = $('#' + entry.elementId + '-table-data');

		var menu = new MenuButton(newElement);
		if (entry.entityType == TABLE_ENTRY) {
			menu.addItem(
				{
					label : "Copy",
					handler : function() { enrichmentsModule.copyTableToClipboard(entry.uuid); }
				}
			);
			if (entry.url) {
				menu.addItem(
					{
						label : "Copy Link",
						handler : function() {
							MendeleyDesktop.module('ui').copyToClipboard(entry.url);
						}
					}
				);
			}
		}
		menu.addItem(
			{
				label : "Report Problem",
				handler : function() {
					enrichmentsModule.reportDataError(entry.uuid);
					var reportNoteElement = $('#' + entry.elementId + ' .error-report-note');
					reportNoteElement.hide();
                    reportNoteElement.text('Thank you for reporting a problem with this ' + typeString);
					reportNoteElement.slideDown();
				}
			}
		);
		menu.createMenu();
	}

	self._currentOutlineElements = function() {
		return $('#section-tables-and-figures > .element-container');
	}

	// update the Tables and Figures sections
	// to display the data from the given entries
	self._populateOutlineEntries = function(entries) {
		self._currentOutlineElements().remove();
		entries.forEach(function(entry, index) {
			self._addOutlineEntry(entry, index);
		});
	}

	// update the 'Mentioned in this Paper' section
	// to display the data from the given entries.
	//
	// Entries are grouped by class label (Algorithm, Corpus etc.)
	// then by distinct mention
	self._populateEntityMentions = function(entries) {
		// remove current entity sections
		var currentMentionGroups = $('#section-list > .named-entity-section');
		currentMentionGroups.remove();

		// group entries by class label,
		// then by URI
		var groups = {};
		entries.forEach(function(entry,index) {
			var label = entry.classLabel;
			var uri = entry.entityUri;
			if (!groups[label]) {
				groups[label] = {};
			}
			if (!groups[label][uri]) {
				groups[label][uri] = [];
			}
			groups[label][uri].push(entry);
		});
		var mentionId = 0;
		var sortedLabels = Object.keys(groups).sort();
		sortedLabels.forEach(function(label, index) {
			if (label == "" || label == "title") {
				return;
			}

			var groupItem = {
				elementId : 'named-entity-group-' + index,
				label : label,
				labelPlural : pluralize(label),
				uniqueEntityCount: Object.keys(groups[label]).length,
				instances : []
			};
			for (var uri in groups[label]) {
				var instances = groups[label][uri];
				var annotIds = [];
				instances.forEach(function(instance) {
					annotIds.push(instance.uuid);
				});

				var shortDescription = UiUtils.elideText(instances[0].description, 80);
				var uriItem = {
					name : instances[0].label,
					shortDescription : shortDescription,
					count : instances.length,
					elementId : 'entity-' + mentionId,
					uri : uri,
					annotIds : annotIds,
					uuid : annotIds[0]
				};
				if (uriItem.name != "") {
					groupItem.instances.push(uriItem);
				}
				++mentionId;
			}
			groupItem.instances.sort(function(a,b) {
				if (a.name < b.name) {
					return -1;
				} else if (a.name > b.name) {
					return 1;
				} else {
					return 0;
				}
			});
			var groupTemplate = ich.named_entity_section(groupItem, {});
			$('#end-of-list').before(groupTemplate);
			var groupElement = $('#' + groupItem.elementId);

			// create sections for each named entity
			groupItem.instances.forEach(function(instance) {
				var instanceTemplate = ich.named_entity_template(instance);
				var result = $(groupElement).append(instanceTemplate);
				var instanceElement = $('#' + instance.elementId);

				instanceElement.mousedown(function() {
					enrichmentsModule.select(instance.annotIds);
				});
				instanceElement.dblclick(function() {
					enrichmentsModule.showAnnotationsInViewer();
				});

				var menuButtonElement = instanceElement.children('.actions-button');
				var menu = new MenuButton(instanceElement);
				menu.createMenu();
			});
		});
	}

	// filter a set of entries to return only the kinds
	// listed in the 'types' array
	self._filterAnnotations = function(entries, types) {
		var matches = [];
		entries.forEach(function(entry,index) {
			if (types.indexOf(entry.entityType) !== -1) {
				matches.push(entry);
			}
		});
		return matches;
	}

	/** Update the view with the current set of entity annotations.
	 * If no annotations are available, the view is hidden and
	 * an overlay is displayed to indicate that no tables/figures etc.
	 * are available.
	 */
	self.update = function() {
		var allEntries = enrichmentsModule.entries.annotations;
		var outlineEntries = self._filterAnnotations(allEntries, [OUTLINE_ENTRY, TABLE_ENTRY, FIGURE_ENTRY]);
		var namedEntities = self._filterAnnotations(allEntries, [SYSTEM_ENTRY]);

		self._populateOutlineEntries(outlineEntries);
		self._populateEntityMentions(namedEntities);

		$('#section-tables-and-figures').toggle(outlineEntries.length > 0);

		self._refreshSelection();
	}

	self._refreshSelection = function() {
		self.updateSelection(enrichmentsModule.selectedAnnotationIds);
	}

	// scroll the annotation list so that the specified annotation
	// element is visible
	self._scrollIntoView = function(element) {
		var container = $('#section-list');

		// calculate offset of annotation element relative
		// to top of annotation list
		var offset = element.offset().top - container.offset().top;
		if (offset < 0) {
			// element is above view, scroll up
			container.scrollTop(container.scrollTop() + offset);
		}
		var bottomOffset = element.offset().top + element.height();
		var containerBottomOffset = container.offset().top + container.height();
		var delta = bottomOffset - containerBottomOffset;
		if (delta > 0) {
			// element is below view, scroll down
			container.scrollTop(container.scrollTop() + delta);
		}
	}

	/** Set the selected elements in the outline list to
	 * those with the given @p ids
	 */
	self.updateSelection = function(ids) {
		if (self._selectedOutlineElements.length > 0) {
			self._selectedOutlineElements.forEach(function(element) {
				$(element).parent().removeClass('selected');
			});
		}
		var topSelectedElement = null;
		self._selectedOutlineElements = [];
		ids.forEach(function(id) {
			var match = $("div[data-uuid='" + id + "']");
			match.each(function(index, element) {
				self._selectedOutlineElements.push(element);
				$(element).parent().addClass('selected');
				topSelectedElement = $(element);
			});
		});
		if (topSelectedElement) {
			self._scrollIntoView(topSelectedElement.parent());
		}
	}
}

/** Implements the outline fetch status overlay which appears
 * when entity annotations are being fetched.
 */
var StatusBar = function() {
	var self = this;

	this._progressTimerId = -1;

	/** Show the overlay with the given @p text */
	this.show = function(text, showThrobber) {
		if (showThrobber) {
			// show a progress indicator if the outline fetch takes longer
			// than several hundred ms.
			self._progressTimerId = setTimeout(function() {
				self._progressThrobber = new Throbber({
					size : 16,
					color : '#666'
				}).appendTo(document.getElementById('enrichments-fetch-progress-throbber'))
				  .start();
			}, 300);
		} else {
			self.stopThrobber();
		}
		$('#enrichments-status-label').text(text);
	};

	this.stopThrobber = function() {
		if (self._progressTimerId != -1) {
			window.clearTimeout(self._progressTimerId);
			self._progressTimerId = -1;
			if (self._progressThrobber) {
				self._progressThrobber.stop();
			}
		}
	};

	this.hide = function() {
		self.stopThrobber();
	};
};

function showFetchStatus(statusLabel) {
	if (!enrichmentsModule.isFetching) {
		statusLabel.show('No enrichments available', false /* hide throbber */);
	} else {
		statusLabel.show('Fetching enrichments information', true /* show throbber */);
	}

	var showList = enrichmentsModule.isFetching || enrichmentsModule.entries.annotations.length > 0;
	$('#section-list').toggle(showList);
	$('#no-enrichments-view').toggle(!showList);
}

var debouncer = new UiUtils.Debouncer();

// work around a crash in QtWebKit 2.2 when JS functions
// connected to signals are invoked (WebKit bug #82383, MD-19914)
//
// The crash occurs due an invalid object being inserted into
// the scope chain for the function and the crash occurs if the JS
// engine walks up the scope chain as far as that object.
//
// This workaround avoids the issue by altering the scope
// chain in which the callback is invoked.
//
// The problem is resolved upstream in QtWebKit 2.3
//
// Usage: someQtObject.signal.connect(qtwebkitSignalWorkaround(callback))
function qtwebkitSignalWorkaround(callback) {
	return function() {
		callback.apply(this, arguments);
	}
}

$(document).ready(function() {
	enrichmentsModule = MendeleyDesktop.module('enrichments');

	var imageExtractor = new PdfImageExtractor(enrichmentsModule);
	var statusBar = new StatusBar();
	var outlineView = new OutlineView(imageExtractor);

	var updateFetchStatus = function() {
		showFetchStatus(statusBar);
	}

	// set to true if an update was deferred because
	// the enrichments tab was not visible
	var updatePending = false;

	var onShow = function() {
		if (updatePending) {
			scheduleTableOfContentsUpdate();
		}
	}

	var scheduleTableOfContentsUpdate = function() {
		if (!enrichmentsModule.isPaneVisible) {
			updatePending = true;
			return;
		}
		updatePending = false;
		debouncer.schedule(0, function() {
			outlineView.update();
		});
	};

	enrichmentsModule.entries.noteAdded.connect(qtwebkitSignalWorkaround(scheduleTableOfContentsUpdate));
	enrichmentsModule.entries.noteRemoved.connect(qtwebkitSignalWorkaround(scheduleTableOfContentsUpdate));
	enrichmentsModule.statusChanged.connect(qtwebkitSignalWorkaround(updateFetchStatus));
	enrichmentsModule.fileChanged.connect(qtwebkitSignalWorkaround(scheduleTableOfContentsUpdate));
	enrichmentsModule.selectedAnnotationsChanged.connect(qtwebkitSignalWorkaround(function(ids) {
		outlineView.updateSelection(ids);
	}));
	enrichmentsModule.paneShown.connect(qtwebkitSignalWorkaround(onShow));

	updateFetchStatus();
	scheduleTableOfContentsUpdate();
});
