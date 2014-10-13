// mendeley.js provides the entry point for Mendeley Desktop
// to invoke citation and bibliography formatting using citeproc-js

CSL.Node["#comment"] = {
	build: function (state, target) {
		// Should never reach this point, in QtWebKit it happens.
	}
};

// MendeleySys provides an interface for the CSL processor
// to retrieve individual citations, locales and abbreviations
// on-demand
MendeleySys = function(){
};

MendeleySys.prototype.retrieveItem = function(id){
	return jsonDocuments[id];
};

MendeleySys.prototype.retrieveLocale = function(lang){
	return locale["en-US"];
	// At the moment, Mendeley Desktop always uses en-US. When we
	// will add support for different locales we will change it.
	// return locale[lang];
};

MendeleySys.prototype.getAbbreviation = function(dummy, obj, jurisdiction, vartype, key){
	if (vartype == "container-title") {
		obj["default"][vartype][key] = MendeleyDesktop.getAbbreviation(key);
	}
};

MendeleySys.prototype.stringCompare = function(a, b) {
	return MendeleyDesktop.localeAwareCaseInsensitiveStringCompare(a,b);
};

// By default citeproc-js formats some output with div classes "csl-entry", "csl-left-margin", etc.
// Instead we change the citeproc-js HTML format to the one that Mendeley plugins use.
// The original citeproc-js output is defined in citeproc.js src/formats.js
var enableMendeleyOutput = function() {
	CSL.Output.Formats["html"]["@bibliography/entry"] = function (state, str) {
		return str;
	}

	CSL.Output.Formats["html"]["@display/right-inline"] = function (state, str) {
		return str;
	}

	CSL.Output.Formats["html"]["@display/left-margin"] = function (state, str) {
		return "<second-field-align>" + str + "</second-field-align>";
	}
	processCitations.style = "";
}

// process a list of citation clusters and generate a list of formatted citations
// and a bibliography
var processCitations = function(clusterCount,enumerateCitations){
	try
	{
		// re-use the existing citeproc-js engine if possible, unless:
		//
		// 1. The citation style has changed OR
		// 2. Multiple citation clusters are being processed (this is required
		//    to work around a bug with restoreProcessorState() not resetting the
		//    disambiguation-related state in citeproc-js.  See trac #18226.)

		if ("undefined" === typeof processCitations.citeproc ||
		    processCitations.style != style ||
		    clusterCount > 1)
		{
			var sys = new MendeleySys();
			processCitations.citeproc = new CSL.Engine(sys, style);
			processCitations.style = style;
			processCitations.citeproc.setAbbreviations("default");
		}
		else
		{
			processCitations.citeproc.restoreProcessorState([]);
		}

		// Clears the abbreviation cache
		processCitations.citeproc.transform.abbrevs = new CSL.AbbreviationSegments();

		for (var cluster = 0; cluster < clusterCount; cluster++)
		{
			var citations = processCitations.citeproc.appendCitationCluster(citationsItems[cluster],false);

			for (var i = 0; i < citations.length; i++)
			{
				var pos = citations[i][0];
				MendeleyDesktop.setCitation(citations[i][0], citations[i][1], citationsItems[pos].citationId);
			}
		}
		
		var makeBibliographyArgument;
		if (enumerateCitations == true)
		{
			makeBibliographyArgument = undefined;
		}
		else
		{
			makeBibliographyArgument = "citation-number";
		}
		var bibliography = processCitations.citeproc.makeBibliography(makeBibliographyArgument);

		var hangingindent = false;
		var has_bibliography = (bibliography !== false);

		if (has_bibliography)
		{
			hangingindent = (bibliography[0].hangingindent != 0 && "undefined" !== typeof(bibliography[0].hangingindent)); // if hanging indent is not 0 it's indented		//alert(bibliography[0].hangingindent);
			bibliography = bibliography[1];
		}
		else
		{
			bibliography = [[(citations[0][1])]];
		}

		MendeleyDesktop.setBibliography(bibliography, hangingindent, has_bibliography);
	}
	catch(err)
	{
		CSL.error("Exception: " + err);
	}
};

var citeprocVersion = function()
{
	return CSL.PROCESSOR_VERSION;
};

enableMendeleyOutput();
