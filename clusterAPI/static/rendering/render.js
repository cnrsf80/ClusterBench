///<reference path="babylon.d.ts" />
var _VISIBLE = 0.9;
var _HIDDEN = 0.08;
var _SIZE = 50;
var ScatterPlot;
var showAxis;
function toString(obj) {
    var s = "";
    var i = 0;
    for (var p in obj) {
        i++;
        var ss = "" + obj[p];
        if (ss.length > 5)
            ss = ss.substr(0, 5);
        s = s + i + ":" + p + "=" + ss + "\n";
    }
    return s;
}
var Game = /** @class */ (function () {
    function Game(canvasElement) {
        this.spheres = [];
        this.links = [];
        this.polygons = [];
        this.scale = _SIZE;
        // Create canvas and engine.
        this._canvas = document.getElementById(canvasElement);
        this._engine = new BABYLON.Engine(this._canvas, true);
        if (BABYLON.VideoRecorder.IsSupported(this._engine))
            this._recorder = new BABYLON.VideoRecorder(this._engine);
    }
    Game.prototype.showCluster = function (cluster_name, show, explicit) {
        if (show === void 0) { show = true; }
        if (explicit === void 0) { explicit = true; }
        if (cluster_name == null)
            cluster_name = "";
        for (var _i = 0, _a = this.spheres; _i < _a.length; _i++) {
            var s = _a[_i];
            var name = s.cluster_name.substr(0, Math.min(cluster_name.length, s.cluster_name.length)).toLowerCase();
            if (name == cluster_name.toLowerCase() && (explicit == false || name.length == cluster_name.length)) {
                if (show)
                    s.material.alpha = _VISIBLE;
                else
                    s.material.alpha = _HIDDEN;
            }
        }
        this.showEdge();
    };
    Game.prototype.showMesure = function (mes_name, show) {
        if (show === void 0) { show = true; }
        for (var _i = 0, _a = this.spheres; _i < _a.length; _i++) {
            var s = _a[_i];
            var name = s.name.substr(0, Math.min(mes_name.length, s.name.length)).toLowerCase();
            if (name == mes_name.toLowerCase())
                if (show)
                    s.material.alpha = _VISIBLE;
                else
                    s.material.alpha = _HIDDEN;
        }
        this.showEdge();
    };
    Game.prototype.showEdge = function () {
        var _this = this;
        this.links.forEach(function (l) {
            if (_this.spheres[l.start].material.alpha == _HIDDEN || _this.spheres[l.end].material.alpha == _HIDDEN)
                l.material.alpha = _HIDDEN;
            else
                l.material.alpha = _VISIBLE;
        });
    };
    Game.prototype.prepareButton = function (mesh) {
        var _this = this;
        mesh.actionManager = new BABYLON.ActionManager(this._scene);
        mesh.actionManager.registerAction(new BABYLON.ExecuteCodeAction({
            trigger: BABYLON.ActionManager.OnPickTrigger
        }, function (evt) {
            var target = evt.meshUnderPointer;
            if (target == null)
                return;
            if (!evt.sourceEvent.altKey && !evt.sourceEvent.ctrlKey) {
                _this.showCluster(target.cluster_name, !evt.sourceEvent.shiftKey);
            }
            if (evt.sourceEvent.altKey && !evt.sourceEvent.ctrlKey) {
                for (var _i = 0, _a = _this.spheres; _i < _a.length; _i++) {
                    var s = _a[_i];
                    if (s.name == target.name) {
                        if (s.increase) {
                            s.scaling = new BABYLON.Vector3(1, 1, 1);
                            s.increase = false;
                        }
                        else {
                            s.scaling = new BABYLON.Vector3(2, 2, 2);
                            s.increase = true;
                        }
                    }
                }
            }
            if (evt.sourceEvent.ctrlKey && !evt.sourceEvent.altKey) {
                for (var _b = 0, _c = _this.spheres; _b < _c.length; _b++) {
                    var s = _c[_b];
                    if (s.ref_cluster == target.ref_cluster) {
                        if (s.increase) {
                            s.scaling = new BABYLON.Vector3(1, 1, 1);
                            s.increase = false;
                        }
                        else {
                            s.scaling = new BABYLON.Vector3(2, 2, 2);
                            s.increase = true;
                        }
                    }
                }
            }
            if (evt.sourceEvent.ctrlKey && evt.sourceEvent.altKey) {
                var index = _this.spheres.indexOf(target);
                if (target.material.alpha == _VISIBLE)
                    _this.spheres[index].material.alpha = _HIDDEN;
                else
                    _this.spheres[index].material.alpha = _VISIBLE;
            }
        }));
        mesh.actionManager.registerAction(new BABYLON.ExecuteCodeAction({
            trigger: BABYLON.ActionManager.OnDoublePickTrigger
        }, function (evt) {
            var target = evt.meshUnderPointer;
            _this.showCluster(null, false);
            _this.showCluster(target.cluster_name);
            _this.setCameraToTarget(target.position.x, target.position.y, target.position.z);
        }));
        mesh.actionManager.registerAction(new BABYLON.ExecuteCodeAction({
            trigger: BABYLON.ActionManager.OnPickDownTrigger
        }, function (evt) {
            game.stopAutoRotation();
        }));
        mesh.actionManager.registerAction(new BABYLON.ExecuteCodeAction({
            trigger: BABYLON.ActionManager.OnPointerOverTrigger
        }, function (evt) {
            var target = evt.meshUnderPointer;
            document.getElementById("row1").innerText = target.name;
            document.getElementById("row2").innerText = target.cluster_name;
            document.getElementById("row4").innerText = target.ref_cluster;
            document.getElementById("row6").innerText = target.index;
            document.getElementById("row5").innerText = toString(target.params);
            document.getElementById("row3").innerText =
                Math.round(target.position.x * 100) / 100 + "," +
                    Math.round(target.position.y * 100) / 100 + "," +
                    Math.round(target.position.z * 100) / 100;
        }));
        mesh.actionManager.registerAction(new BABYLON.ExecuteCodeAction({
            trigger: BABYLON.ActionManager.OnPointerOutTrigger
        }, function (evt) {
            var target = evt.meshUnderPointer;
            for (var i = 1; i < 6; i++)
                document.getElementById("row" + i).innerText = "";
        }));
    };
    Game.prototype.createMesure = function (obj) {
        var materialSphere = new BABYLON.StandardMaterial("texture2", this._scene);
        materialSphere.diffuseColor = new BABYLON.Color3(obj.style[0], obj.style[1], obj.style[2]);
        materialSphere.alpha = 0.9;
        obj.style = null;
        var sphere = BABYLON.MeshBuilder.CreateSphere(name, { segments: 16, diameter: obj.size }, this._scene);
        sphere.position.x = (obj.x) * this.scale;
        obj.x = null;
        sphere.position.y = (obj.y) * this.scale;
        obj.y = null;
        sphere.position.z = (obj.z) * this.scale;
        obj.z = null;
        sphere.material = materialSphere;
        sphere.cluster_name = obj.cluster;
        obj.cluster = null;
        sphere.ref_cluster = obj.ref_cluster;
        obj.ref_cluster = null;
        sphere.name = obj.name;
        obj.name = null;
        sphere.label = obj.name;
        obj.label = null;
        sphere.index = obj.index;
        obj.index = null;
        sphere.size = obj.size;
        obj.size = null;
        sphere.params = {};
        //Certaines propriétés sont supprimées du paramétres de la sphere (voir traitement suivant)
        obj.form = null;
        obj.Ref = null;
        obj.cluster_distance = null;
        for (var p in obj) {
            if (obj[p] != null && sphere.params[p] == null)
                sphere.params[p] = obj[p];
        }
        if (obj.hasOwnProperty("cluster_distance"))
            sphere.cluster_distance = JSON.parse(obj.cluster_distance);
        this.prepareButton(sphere);
        this.spheres[sphere.index] = sphere;
    };
    Game.prototype.linkSphere = function (s1, s2, radius) {
        if (radius === void 0) { radius = 0.04; }
        var path = [
            new BABYLON.Vector3(s1.position.x, s1.position.y, s1.position.z),
            new BABYLON.Vector3(s2.position.x, s2.position.y, s2.position.z)
        ];
        var tube = BABYLON.MeshBuilder.CreateTube("link" + s1.name + "_" + s2.name, {
            path: path,
            radius: radius,
            tessellation: 8,
        }, this._scene);
        tube.material = new BABYLON.StandardMaterial("texture2", this._scene);
        tube.material.diffuseColor = new BABYLON.Color3(0.9, 0.9, 0.9);
        tube.material.alpha = _VISIBLE;
        tube["start"] = s1.index;
        tube["end"] = s2.index;
        this.links.push(tube);
    };
    Game.prototype.getVisibleClusters = function () {
        var rc = [];
        this.spheres.forEach(function (s) {
            if (s.material.alpha == _VISIBLE && rc.indexOf(s.cluster_name) == -1)
                rc.push(s.cluster_name);
        });
        return rc;
    };
    Game.prototype.createScene = function () {
        // Create a basic BJS Scene object.
        this._scene = new BABYLON.Scene(this._engine);
        this._scene.fogMode = BABYLON.Scene.FOGMODE_EXP;
        this._scene.fogDensity = 0.0015;
        this._scene.fogColor = new BABYLON.Color3(0.95, 0.95, 0.95);
        this._scene.clearColor = new BABYLON.Color4(0.9, 0.9, 0.9);
        this._scene.registerBeforeRender(function () {
        });
        var dim = this.scale * 2;
        // var scatterPlot = new ScatterPlot([dim,dim,dim],{
        //     x: ["", "0", "1","2"],
        //     y: ["", "0", "1","2"],
        //     z: ["2","1", "0", "-1"]
        // }, this._scene);
        showAxis(50, this._scene);
        // Create a FreeCamera, and set its position to (x:0, y:5, z:-10).
        this._camera = new BABYLON.ArcRotateCamera("Camera", 2.2 * Math.PI / 2, 1.5 * Math.PI / 2, this.scale * 1.5, BABYLON.Vector3.Zero(), this._scene);
        this._actionManager = new BABYLON.ActionManager(this._scene);
        // Target the camera to scene origin.
        this._camera.setTarget(new BABYLON.Vector3(0, 0, 0));
        // Attach the camera to the canvas.
        this._camera.attachControl(this._canvas, false);
        // Create a basic light, aiming 0,1,0 - meaning, to the sky.
        this._light1 = new BABYLON.HemisphericLight('light1', new BABYLON.Vector3(0, 0, -20), this._scene);
        this._light2 = new BABYLON.HemisphericLight('light2', new BABYLON.Vector3(0, 0, +20), this._scene);
        this._light1.intensity = 0.65;
        this._light2.intensity = 0.65;
        if (location.href.indexOf("autorotate") > -1)
            this.startAutoRotation();
        // Create a built-in "ground" shape.
        //let ground = BABYLON.MeshBuilder.CreateGround('ground1',{width: 6, height: 6, subdivisions: 2}, this._scene);
    };
    Game.prototype.doRender = function () {
        var _this = this;
        // Run the render loop.
        this._engine.runRenderLoop(function () {
            _this._scene.render();
        });
        // The canvas/window resize event handler.
        window.addEventListener('resize', function () {
            _this._engine.resize();
        });
    };
    Game.prototype.clearMesures = function (nMesures) {
        this.spheres.forEach(function (s) { s.dispose(); });
        this.spheres = [];
        while (nMesures > 0) {
            this.spheres.push({});
            nMesures--;
        }
        this.clearLinks();
    };
    Game.prototype.makeRotate = function () {
        this._camera.alpha = game._camera.alpha + 0.1;
        this._camera.rebuildAnglesAndRadius();
        this.doRender();
    };
    Game.prototype.getVisibleMesure = function () {
        var l = [];
        this.spheres.forEach(function (s) {
            if (s.material.alpha == _VISIBLE) {
                l.push(s);
            }
        });
        return l;
    };
    Game.prototype.showClosedCluster = function () {
        var _this = this;
        var l = this.getVisibleMesure();
        l.forEach(function (s) {
            var i = 0;
            for (var k in s.cluster_distance) {
                var d = s.cluster_distance[k];
                i++;
                if (i > 5)
                    break;
                _this.spheres[d.p1].material.alpha = _VISIBLE;
                _this.spheres[d.p2].material.alpha = _VISIBLE;
                _this.linkSphere(_this.spheres[d.p1], _this.spheres[d.p2]);
            }
        });
    };
    /**
     * Trace les facettes
     * @param clusters
     * @param translate
     * @param expense
     * @param filter
     * @param offset contient le numero du graphique
     */
    Game.prototype.traceFacets = function (clusters, translate, filter, offset) {
        var _this = this;
        if (offset === void 0) { offset = 0; }
        clusters.forEach(function (facets) {
            facets.forEach(function (facet) {
                if (facet[1] == offset && (filter == null || facet[0].indexOf(filter) > -1)) {
                    var positions = [];
                    facet[3].forEach(function (f) {
                        var s = _this.spheres[f];
                        s.position.index = s.index;
                        positions.push(s.position);
                    });
                    var shape = [
                        new BABYLON.Vector3(positions[0].x, positions[0].y, positions[0].z),
                        new BABYLON.Vector3(positions[1].x, positions[1].y, positions[1].z),
                        new BABYLON.Vector3(positions[2].x, positions[2].y, positions[2].z)
                    ];
                    var lines = [[shape[0], shape[1]], [shape[1], shape[2]], [shape[0], shape[2]]];
                    var polygon = BABYLON.MeshBuilder.CreateLineSystem("line" + facet[0], { lines: lines }, _this._scene);
                    polygon.color = new BABYLON.Color3(facet[2][0], facet[2][1], facet[2][2]);
                    _this.polygons.push(polygon);
                }
            });
        });
    };
    Game.prototype.removeFacets = function () {
        this.polygons.forEach(function (p) {
            p.dispose();
        });
        this.polygons = [];
    };
    Game.prototype.clearLinks = function () {
        this.links.forEach(function (l) { l.dispose(); });
        this.links = [];
    };
    Game.prototype.removeNoise = function () {
        var _this = this;
        var toRemove = [];
        this.spheres.forEach(function (s) {
            if (s.cluster_name == "noise") {
                s.dispose();
                toRemove.push(_this.spheres.indexOf(s));
            }
        });
    };
    Game.prototype.mesureConnection = function (edges) {
        var _this = this;
        if (edges === void 0) { edges = null; }
        if (false) {
            this.getVisibleMesure().forEach(function (m) {
                if (m.cluster_name != "noise") {
                    _this.spheres.forEach(function (s) {
                        if (s.ref_cluster == m.ref_cluster && s.cluster_name != "noise")
                            _this.linkSphere(s, m);
                    });
                }
            });
        }
        else {
            edges.forEach(function (e) {
                _this.linkSphere(_this.spheres[e.start], _this.spheres[e.end]);
            });
        }
    };
    Game.prototype.startAutoRotation = function () {
        this._camera.useAutoRotationBehavior = true;
        this._camera.autoRotationBehavior.idleRotationSpeed = 0.4;
    };
    Game.prototype.stopAutoRotation = function () {
        this._camera.useAutoRotationBehavior = false;
    };
    Game.prototype.isRotating = function () {
        return (this._camera.useAutoRotationBehavior);
    };
    Game.prototype.makeMovie = function () {
        document.getElementById("message").innerHTML = "<img style='width:20px' src='https://api.voxhub.net/api-v1/contentFileLoader?file=/website/store/recordings/df85aa22-4888-465d-8976-5739eec9f415'>";
        this._recorder.startRecording("clusterBench.webm", 400);
    };
    Game.prototype.stopMovie = function () {
        document.getElementById("message").innerHTML = "";
        this._recorder.stopRecording();
    };
    Game.prototype.message = function (s, delayInSec) {
        if (delayInSec === void 0) { delayInSec = 10; }
        document.getElementById("message").innerHTML = s;
        setTimeout(function () {
            document.getElementById("message").innerHTML = "";
        }, delayInSec * 1000);
    };
    Game.prototype.setCameraToTarget = function (x, y, z) {
        this._camera.setTarget(new BABYLON.Vector3(Number(x), Number(y), Number(z)));
    };
    Game.prototype.updateScale = function (step, datas, edges) {
        var _this = this;
        this.clearLinks();
        this.spheres.forEach(function (s) {
            s.position.x = s.position.x * step;
            s.position.y = s.position.y * step;
            s.position.z = s.position.z * step;
        });
        edges.forEach(function (e) {
            _this.linkSphere(_this.spheres[e.start], _this.spheres[e.end]);
        });
    };
    Game.prototype.toCSV = function (datas, sep, end_line) {
        if (sep === void 0) { sep = ";"; }
        if (end_line === void 0) { end_line = "\n"; }
        //Créer la ligne des mesures
        if (datas.length == 0)
            return ("");
        var rc = "Names" + sep;
        for (var k = 0; k < datas[0].length - 1; k++)
            rc = rc + "Mesure" + k + sep;
        rc = rc.substr(0, rc.length - 1) + end_line;
        var i = 0;
        this.spheres.forEach(function (s) {
            if (s.material.alpha == _VISIBLE) {
                rc = rc + datas[i].join(sep) + end_line;
            }
            i++;
        });
        return rc;
    };
    Game.prototype.setSizeTo = function (n_prop) {
        var max = -1000;
        this.spheres.forEach(function (s) {
            var v = Number(Object.values(s.params)[n_prop - 1]);
            if (v > max)
                max = v;
        });
        var fact = 8 / max;
        this.spheres.forEach(function (s) {
            if (n_prop == null)
                s.scaling = new BABYLON.Vector3(1, 1, 1);
            else {
                var v = Number(Object.values(s.params)[n_prop - 1]);
                if (v > 0 && v <= 1)
                    s.scaling = new BABYLON.Vector3(fact * v, fact * v, fact * v);
            }
        });
    };
    Game.prototype.propage = function (alpha) {
        var _this = this;
        var l_s = [];
        this.links.forEach(function (l) {
            var s1 = _this.spheres[l.start];
            var s2 = _this.spheres[l.end];
            if (s1.material.alpha != s2.material.alpha) {
                l_s.push(s1);
                l_s.push(s2);
            }
        });
        l_s.forEach(function (s) { s.material.alpha = alpha; });
        this.showEdge();
    };
    return Game;
}());
var game = null;
window.addEventListener('DOMContentLoaded', function () {
    // Create the game using the 'renderCanvas'.
    game = new Game('renderCanvas');
    // Create the scene.
    game.createScene();
    // Start render loop.
    game.doRender();
});
var facets = [];
var facets_ref = [];
var datas = null;
var data_source = null;
var edges = [];
/**
 * Affichage des points contenu dans datas
 */
window.addEventListener("message", function (evt) {
    datas = evt.data.datas;
    data_source = evt.data.data_source;
    evt.preventDefault();
    if (datas != null && datas.length > 0) {
        game.clearMesures(datas.length);
        var i = 0;
        game.message("Création de " + datas.length + " mesures", 2);
        for (var _i = 0, datas_1 = datas; _i < datas_1.length; _i++) {
            var p = datas_1[_i];
            game.createMesure(p);
        }
        if (evt.data.autorotate)
            game.startAutoRotation();
        facets = evt.data.facets;
        facets_ref = evt.data.facets_ref;
        edges = evt.data.edges;
        game.mesureConnection(edges);
    }
}, false);
function download(text, name, type) {
    var a = document.getElementById("a");
    var file = new Blob([text], { type: type });
    a.href = URL.createObjectURL(file);
    a.download = name;
}
window.addEventListener("keypress", function (evt) {
    if (evt.key == "c") {
        game.showCluster(prompt("Cluster name"), true, false);
    }
    if (evt.key == "C") {
        game.showCluster(prompt("Cluster name"), false);
    }
    if (evt.key == "N") {
        game.showCluster("noise", false);
    }
    if (evt.key == "+")
        game.updateScale(1.05, datas, edges);
    if (evt.key == "-")
        game.updateScale(0.95, datas, edges);
    if (evt.key == "n") {
        game.showCluster("noise", true);
    }
    if (evt.key == "S") {
        //game.clearLinks();
        game.showCluster("", false);
    }
    if (evt.key == "p") {
        game.getVisibleClusters().forEach(function (c) {
            var url = location.href.split("offset=")[1];
            game.traceFacets(facets, 0, c, Number(url));
        });
    }
    if (evt.key == "o") {
        var url = location.href.split("offset=")[1];
        game.traceFacets(facets_ref, 0, null, Number(url));
    }
    if (evt.key == "H") {
        document.getElementById("message").innerHTML = "";
    }
    if (evt.key == "x")
        game.propage(_VISIBLE);
    if (evt.key == "X")
        game.propage(_HIDDEN);
    if (evt.key == "h") {
        var text = "" +
            "            <h3>Commandes sur la visu 3d:</h3>>" +
            "            - <strong>'s'</strong> et SHIFT+'s' respectivement montre et cache toutes les mesures<br>\n" +
            "            - <strong>'m'</strong> et SHIFT+'m' opere un filtre sur les mesures pour les montrer / cacher<br>\n" +
            "            - <strong>'c'</strong> et SHIFT+'c' opere un filtre sur les clusters pour les montrer / cacher<br>\n" +
            "            - <strong>'a'</strong> et SHIFT+'a' engage une autorotation du graphique<br>\n" +
            "            - <strong>'w'</strong> centre la caméra sur l'échantillon pointé par la souris<br>\n" +
            "            - <strong>'v'</strong> et SHIFT+'v' démarre et stop un enregistrement video au format webm (lisible par vlc ou d'autres lecteurs)<br>\n" +
            "            - <strong>'+'</strong> et '-' écarte/réduit les mesure par changement d'échelle <br>\n" +
            "            - <strong>'e'</strong> export les données visibles au format CSV dans le presse papier<br>\n" +
            "            - <strong>'p'</strong> et SHIFT+'p' entoure les clusters visible (patatoides) <br>\n" +
            "            - <strong>'x'</strong> et SHIFT+'x' propagation des mesures visiblesh / cachées <br>\n" +
            "            - <strong>'o'</strong> entoure les clusters de référence<br>\n" +
            "            - <strong>'r'</strong> supprime définitivement le bruit (permet d'accéler la navigation)<br>\n" +
            "            - <strong>'k'</strong> connecte entre elles les mesures du même nom<br>\n" +
            "\n" +
            "            - 'click' et 'SHIFT+click' montre / cache le cluster d'appartenance de la mesure<br>\n" +
            "            - 'double click' permet d'étudier un cluster en particulier<br>\n" +
            "            - 'ALT+click' permet grossis / réduit les mesures du même nom<br>\n" +
            "            - 'click droit' permet d'enregistrer la visu en format image";
        game.message(text, 10);
    }
    if (evt.key == "P") {
        game.removeFacets();
    }
    if (evt.key == "w") {
        var txt = document.getElementById("row3").innerText;
        if (txt != null && txt.length > 0) {
            var coord = txt.split(",");
            game.setCameraToTarget(coord[0], coord[1], coord[2]);
        }
    }
    if (evt.key == "W") {
        game.setCameraToTarget("0", "0", "0");
    }
    if (evt.key == "s") {
        game.showCluster("", true);
    }
    if (evt.key == "d") {
        game.clearLinks();
        game.showClosedCluster();
    }
    if (evt.key == "v") {
        game.makeMovie();
    }
    if (evt.key == "V") {
        game.stopMovie();
    }
    if (evt.key == "a") {
        if (game.isRotating())
            game.stopAutoRotation();
        else
            game.startAutoRotation();
    }
    if (evt.key == "A")
        game.stopAutoRotation();
    if (evt.key == "e") {
        var code = game.toCSV(data_source);
        // @ts-ignore
        navigator.permissions.query({ name: "clipboard-write" }).then(function (result) {
            if (result.state == "granted" || result.state == "prompt") {
                // @ts-ignore
                navigator.clipboard.writeText(code).then(function () {
                    alert("Mesures visible dans le presse-papier au format CSV");
                });
            }
            else {
                prompt("Copier dans le presse papier", code);
            }
        });
    }
    if (evt.key == "E") {
        var code = game.toCSV(data_source);
        fetch("./measure/temp.csv", { method: "POST", body: code }).then(function (r) {
            debugger;
        }).catch((function (err) {
            debugger;
        }));
    }
    if (evt.key == "k") {
        game.mesureConnection();
    }
    if (evt.key == "m") {
        game.showMesure(prompt("Measure name"), true);
    }
    if (evt.key == "M") {
        game.showMesure(prompt("Measure name"), false);
    }
    if (evt.key == "L") {
        game.clearLinks();
    }
    if ("" + Number(evt.key) == evt.key) {
        if (evt.key == "0")
            game.setSizeTo(null);
        else
            game.setSizeTo(Number(evt.key));
    }
    if (evt.key == "r") {
        game.removeNoise();
    }
});
