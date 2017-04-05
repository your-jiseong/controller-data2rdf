# Data2RDF Controller

Description
-----
Data2RDF Controller is a workflow manager that is to link all of the sub-modules (NER, NED, Text2K, and RDFG) to provide Data2RDF's pipeline as a united service. It is a part of the information extraction framework for the EUROSTAR - QAMEL project.

Prerequisite
-----
The module is working on Python 2.7. It must be prepared to install Python 2.7 and PIP (Python Package Index) before the installation of the module.

How to install
-----
Before executing the module, we need to install all of the dependencies.
To install dependencies, execute the following command.

```
sh dependency.sh
```

Configure a service address of sub-modules (NER, NED, Text2K, and RDFG) by editing "conf.json" as follows.

```
{
	"address": {
		"ner": {
			"en": "http://qamel.kaist.ac.kr:8080/recognition",
			"de": "http://qamel.kaist.ac.kr:8080/recognition",
			"ko": "http://qamel.kaist.ac.kr:2224/entity_linking"
		},
		"ned": {
			"en": "http://qamel.kaist.ac.kr:8080/disambiguation",
			"de": "http://qamel.kaist.ac.kr:8080/disambiguation",
			"ko": "http://qamel.kaist.ac.kr:2224/entity_linking"
		},
		"text2k": {
			"en": "http://qamel.kaist.ac.kr:8080/text2k",
			"de": "http://qamel.kaist.ac.kr:8080/text2k",
			"ko": "http://qamel.kaist.ac.kr:4444/text2k/"
		},
		"rdfg": "http://qamel.kaist.ac.kr:7402/service"
	}
}
```

To execute the module, run the service by the following command.

```
python service.py
```

The address of REST API is as follows.

```
http://server-address:7401/service
```

The module accepts only a POST request which of content type must be "application/json".

AUTHOR(S)
---------
* Jiseong Kim, MachineReadingLab@KAIST

License
-------
Released under the MIT license (http://opensource.org/licenses/MIT).