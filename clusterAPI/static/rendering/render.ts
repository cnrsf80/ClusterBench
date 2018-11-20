///<reference path="babylon.d.ts" />

import float = BABYLON.float;

const _VISIBLE=0.9;
const _HIDDEN=0.2;
const _SIZE=50;

var ScatterPlot:any;
var showAxis:Function;


class Game {

    private spheres:any[]=[];
    private links:any[]=[];
    private polygons:any[]=[];

    private scale=_SIZE;

    private _canvas: HTMLCanvasElement;
    private _engine: BABYLON.Engine;
    private _recorder: BABYLON.VideoRecorder;
    private _scene: BABYLON.Scene;
    private _camera: BABYLON.ArcRotateCamera;
    private _light1: BABYLON.Light;
    private _light2: BABYLON.Light;
    private _actionManager:BABYLON.ActionManager;

    constructor(canvasElement : string) {
        // Create canvas and engine.
        this._canvas = document.getElementById(canvasElement) as HTMLCanvasElement;
        this._engine = new BABYLON.Engine(this._canvas, true);
        if(BABYLON.VideoRecorder.IsSupported(this._engine))
            this._recorder = new BABYLON.VideoRecorder(this._engine)
    }


    showCluster(cluster_name,show=true,explicit=true){
        if(cluster_name==null)cluster_name="";
        for (let s of this.spheres) {
            var name=s.cluster_name.substr(0,Math.min(cluster_name.length,s.cluster_name.length)).toLowerCase();
            if (name == cluster_name.toLowerCase() && (explicit==false || name.length==cluster_name.length)){
                if(show)
                    s.material.alpha = _VISIBLE;
                else
                    s.material.alpha = _HIDDEN;
            }
        }
        //this.showEdge();
    }

    showMesure(mes_name,show=true){
        for (let s of this.spheres) {
            var name=s.name.substr(0,Math.min(mes_name.length,s.name.length)).toLowerCase();
            if (name == mes_name.toLowerCase())
                if(show)
                    s.material.alpha = _VISIBLE;
                else
                    s.material.alpha = _HIDDEN;
        }
        //this.showEdge();
    }

    showEdge(){
        this.links.forEach(l=>{
            if(this.spheres[l.start].material.alpha==_HIDDEN || this.spheres[l.end].material.alpha==_HIDDEN)
                l.edgesColor.alpha=_HIDDEN;
            else
                l.edgesColor.alpha=_VISIBLE;
        });
    }


    prepareButton(mesh) {
        mesh.actionManager = new BABYLON.ActionManager(this._scene);
        mesh.actionManager.registerAction(
            new BABYLON.ExecuteCodeAction(
                {
                    trigger: BABYLON.ActionManager.OnPickTrigger
                },
                (evt) => {

                    let target:any=evt.meshUnderPointer;
                    if(target==null)return;

                    if(!evt.sourceEvent.altKey && !evt.sourceEvent.ctrlKey){
                        this.showCluster(target.cluster_name,!evt.sourceEvent.shiftKey);
                    }


                    if(evt.sourceEvent.altKey){
                        for (let s of this.spheres) {
                            if (s.name == target.name ){
                                if (s.increase) {
                                        s.scaling = new BABYLON.Vector3(1, 1, 1);
                                        s.increase = false;
                                } else {
                                            s.scaling = new BABYLON.Vector3(2, 2, 2);
                                            s.increase=true;
                                        }
                            }
                        }
                    }

                    if(evt.sourceEvent.ctrlKey){
                        for (let s of this.spheres) {
                            if (s.ref_cluster == target.ref_cluster ){
                                if (s.increase) {
                                        s.scaling = new BABYLON.Vector3(1, 1, 1);
                                        s.increase = false;
                                } else {
                                            s.scaling = new BABYLON.Vector3(2, 2, 2);
                                            s.increase=true;
                                        }
                            }
                        }
                    }
                }
            )
        );

        mesh.actionManager.registerAction(
            new BABYLON.ExecuteCodeAction(
                {
                    trigger: BABYLON.ActionManager.OnDoublePickTrigger
                },
                (evt)=>{
                    let target:any=evt.meshUnderPointer;
                    this.showCluster(null,false);
                    this.showCluster(target.cluster_name);
                    this.setCameraToTarget(target.position.x,target.position.y,target.position.z);
                }
            )
        );

        mesh.actionManager.registerAction(
            new BABYLON.ExecuteCodeAction(
                {
                    trigger: BABYLON.ActionManager.OnPickDownTrigger
                },
                (evt) => {
                    game.stopAutoRotation();
                }
            )
        );

        mesh.actionManager.registerAction(
            new BABYLON.ExecuteCodeAction(
                {
                    trigger: BABYLON.ActionManager.OnPointerOverTrigger
                },
                (evt) => {
                    let target:any=evt.meshUnderPointer;
                    document.getElementById("row1").innerText=target.name;
                    document.getElementById("row2").innerText=target.cluster_name;
                    document.getElementById("row4").innerText=target.ref_cluster;
                    document.getElementById("row3").innerText=
                        Math.round(target.position.x*100)/100+","+
                        Math.round(target.position.y*100)/100+","+
                        Math.round(target.position.z*100)/100;
                }
            )
        );

        mesh.actionManager.registerAction(
            new BABYLON.ExecuteCodeAction(
                {
                    trigger: BABYLON.ActionManager.OnPointerOutTrigger
                },
                (evt) => {
                    let target:any=evt.meshUnderPointer;
                    for(var i=1;i<5;i++)
                        document.getElementById("row"+i).innerText="";

                }
            )
        );
    }

    createMesure(obj:any,color:BABYLON.Color3):void {
        var materialSphere = new BABYLON.StandardMaterial("texture2", this._scene);
        materialSphere.diffuseColor = color;
        materialSphere.alpha = 0.9;

        let sphere:any = BABYLON.MeshBuilder.CreateSphere(name,{segments: 16, diameter: 1}, this._scene);

        sphere.position.x = (obj.x)*this.scale;
        sphere.position.y = (obj.y)*this.scale;
        sphere.position.z = (obj.z)*this.scale;
        sphere.material=materialSphere;
        sphere.cluster_name=obj.cluster;
        sphere.ref_cluster=obj.ref_cluster;
        sphere.name=obj.name;
        sphere.index=obj.index;
        if(obj.hasOwnProperty("cluster_distance"))sphere.cluster_distance=JSON.parse(obj.cluster_distance);

        this.prepareButton(sphere);
        this.spheres.push(sphere);
    }

    linkSphere(s1:any,s2:any):void {
        let path = [
            new BABYLON.Vector3(s1.position.x, s1.position.y, s1.position.z),
            new BABYLON.Vector3(s2.position.x, s2.position.y, s2.position.z)
        ];

        var tube:any = BABYLON.MeshBuilder.CreateTube("link"+s1.name+"_"+s2.name,
            {
                path: path,
                radius: 0.04,
                tessellation:12,
            },
            this._scene);

        tube.material=new BABYLON.StandardMaterial("texture2", this._scene);
        tube.material.diffuseColor = new BABYLON.Color3(0.8,0.8,0.8);
        tube.material.alpha = _VISIBLE;

        tube["start"]=s1.index;
        tube["end"]=s2.index;

        this.links.push(tube);
    }

    getVisibleClusters():any[]{
        var rc=[];
        this.spheres.forEach(s=>{
           if(s.material.alpha==_VISIBLE && rc.indexOf(s.cluster_name)==-1)
               rc.push(s.cluster_name)
        });
        return rc;
    }

    createScene() : void {
        // Create a basic BJS Scene object.
        this._scene = new BABYLON.Scene(this._engine);
        this._scene.fogMode = BABYLON.Scene.FOGMODE_EXP;
        this._scene.fogDensity = 0.0015;
        this._scene.fogColor = new BABYLON.Color3(0.95, 0.95, 0.95);
        this._scene.clearColor = new BABYLON.Color4(0.9, 0.9, 0.9);

        this._scene.registerBeforeRender(()=>{

        });

        var dim=this.scale*2;
        // var scatterPlot = new ScatterPlot([dim,dim,dim],{
        //     x: ["", "0", "1","2"],
        //     y: ["", "0", "1","2"],
        //     z: ["2","1", "0", "-1"]
        // }, this._scene);
        showAxis(50,this._scene);

        // Create a FreeCamera, and set its position to (x:0, y:5, z:-10).
        this._camera = new BABYLON.ArcRotateCamera("Camera",
            2.2*Math.PI / 2,
            1.5*Math.PI/2 ,
            this.scale*1.5,
            BABYLON.Vector3.Zero(),
            this._scene);

        this._actionManager = new BABYLON.ActionManager(this._scene);

        // Target the camera to scene origin.
        this._camera.setTarget(new BABYLON.Vector3(0,0,0));

        // Attach the camera to the canvas.
        this._camera.attachControl(this._canvas, false);

        // Create a basic light, aiming 0,1,0 - meaning, to the sky.
        this._light1 = new BABYLON.HemisphericLight('light1', new BABYLON.Vector3(0,0,-20), this._scene);
        this._light2 = new BABYLON.HemisphericLight('light2', new BABYLON.Vector3(0,0,+20), this._scene);
        this._light1.intensity=0.65;
        this._light2.intensity=0.65;


        if(location.href.indexOf("autorotate")>-1)
            this.startAutoRotation();

        // Create a built-in "ground" shape.
        //let ground = BABYLON.MeshBuilder.CreateGround('ground1',{width: 6, height: 6, subdivisions: 2}, this._scene);
    }



    doRender() : void {
        // Run the render loop.
        this._engine.runRenderLoop(() => {
            this._scene.render();
        });

        // The canvas/window resize event handler.
        window.addEventListener('resize', () => {
            this._engine.resize();
        });
    }


    clearMesures() {
        this.spheres=[];
        this.links=[];
    }




    makeRotate(){
        this._camera.alpha=game._camera.alpha+0.1;
        this._camera.rebuildAnglesAndRadius();
        this.doRender();
    }




    getVisibleMesure(){
        var l=[];
        this.spheres.forEach((s:any)=> {
                if (s.material.alpha == _VISIBLE) {
                    l.push(s);
                }
            });
        return l;
    }

    showClosedCluster() {
        let l=this.getVisibleMesure();
        l.forEach((s)=>{
                let i=0;
                for(let k in s.cluster_distance){
                    let d=s.cluster_distance[k];
                    i++;
                    if(i>5)break;
                    this.spheres[d.p1].material.alpha=_VISIBLE;
                    this.spheres[d.p2].material.alpha=_VISIBLE;
                    this.linkSphere(this.spheres[d.p1],this.spheres[d.p2]);
                }
            }
        )
    }

    /**
     * Trace les facettes
     * @param clusters
     * @param translate
     * @param expense
     * @param filter
     * @param offset contient le numero du graphique
     */
    traceFacets(clusters:any[],translate:float,filter:null,offset=0){
        clusters.forEach(facets=>{
            facets.forEach((facet)=>{
                if(facet[1]==offset && (filter==null || facet[0].indexOf(filter)>-1)){
                    var k=3;
                    var shape = [
                            new BABYLON.Vector3((facet[k][0]+translate)*this.scale, (facet[k][1]+translate)*this.scale,(facet[k][2]+translate)*this.scale),
                            new BABYLON.Vector3((facet[k+1][0]+translate)*this.scale, (facet[k+1][1]+translate)*this.scale,(facet[k+1][2]+translate)*this.scale),
                            new BABYLON.Vector3((facet[k+2][0]+translate)*this.scale, (facet[k+2][1]+translate)*this.scale,(facet[k+2][2]+translate)*this.scale)
                      ];


                    var lines=[[shape[0],shape[1]],[shape[1],shape[2]],[shape[0],shape[2]]];
                    var polygon=BABYLON.MeshBuilder.CreateLineSystem(
                        "line"+facet[0],
                        {lines:lines},
                        this._scene);
                    polygon.color=new BABYLON.Color3(facet[2][0],facet[2][1],facet[2][2]);


                this.polygons.push(polygon);
                }
            });
        })
    }

    removeFacets(){
        this.polygons.forEach(p=>{
            p.dispose();
        });

        this.polygons=[];
    }

    clearLinks() {
        this.links.forEach((l)=>{
            l.dispose();
        });
        this.links=[];
    }

    removeNoise() {
        var toRemove=[];
        this.spheres.forEach((s)=>{
            if(s.cluster_name=="noise"){
                s.dispose();
                toRemove.push(this.spheres.indexOf(s));
            }
        });
    }

    mesureConnection(edges=null) {
        if(false){
            this.getVisibleMesure().forEach((m)=>{
                if(m.cluster_name!="noise"){
                    this.spheres.forEach((s)=>{
                       if(s.ref_cluster==m.ref_cluster && s.cluster_name!="noise")
                           this.linkSphere(s,m);
                    });
                }
            });
        } else {
            edges.forEach(e=>{
                this.linkSphere(this.spheres[e.start],this.spheres[e.end]);
            });
        }

    }

    startAutoRotation(){
        this._camera.useAutoRotationBehavior=true;
        this._camera.autoRotationBehavior.idleRotationSpeed=0.4;
    }

    stopAutoRotation(){
        this._camera.useAutoRotationBehavior=false;
    }

    makeMovie() {
        document.getElementById("message").innerHTML="<img style='width:20px' src='https://api.voxhub.net/api-v1/contentFileLoader?file=/website/store/recordings/df85aa22-4888-465d-8976-5739eec9f415'>";
        this._recorder.startRecording("clusterBench.webm",400);
    }

    stopMovie() {
        document.getElementById("message").innerHTML="";
        this._recorder.stopRecording();
    }


    setCameraToTarget(x: string, y: string, z: string) {
        this._camera.setTarget(new BABYLON.Vector3(Number(x),Number(y),Number(z)));
    }

    updateScale(step: number,datas:any[]) {
         this.spheres.forEach((s:any)=> {
            s.position.x=s.position.x*step;
            s.position.y=s.position.y*step;
            s.position.z=s.position.z*step;
         });
    }

    toCSV(datas,sep=";",end_line="\n") {
        //Créer la ligne des mesures
        if(datas.length==0)return("");

        var rc="Ref"+sep;
        for(var k=0;k<datas[0].length-1;k++)rc=rc+"Mesure"+k+sep;
        rc=rc.substr(0,rc.length-1)+end_line;

        var i=0;
        this.spheres.forEach((s:any)=> {
            if(s.material.alpha==_VISIBLE){
                rc=rc+datas[i].join(sep)+end_line;
            }
            i++;
         });
        return rc;
    }
}

let game:Game=null;


window.addEventListener('DOMContentLoaded', () => {
    // Create the game using the 'renderCanvas'.
    game = new Game('renderCanvas');

    // Create the scene.
    game.createScene();

    // Start render loop.
    game.doRender();
});

var facets=[];
var facets_ref=[];
var datas:any=null;
var data_source:any=null;
var edges=[]

/**
 * Affichage des points contenu dans datas
 *
 */
window.addEventListener("message", (evt)=> {
    datas = evt.data.datas;
    data_source=evt.data.data_source;

    evt.preventDefault();
    if (datas!=null && datas.length>0) {
        game.clearMesures();
        var i=0;
        for (let p of datas){
            p.index=i;
            game.createMesure(p,new BABYLON.Color3(p.style[0],p.style[1],p.style[2]));
            i=i+1
        }


        facets=evt.data.facets;
        facets_ref=evt.data.facets_ref;
        edges=evt.data.edges;

        game.mesureConnection(edges);
    }
}, false);


function download(text, name, type) {
  var a:any = document.getElementById("a");
  var file = new Blob([text], {type: type});
  a.href = URL.createObjectURL(file);
  a.download = name;
}


window.addEventListener("keypress", (evt)=> {
   if(evt.key=="c"){
       game.showCluster(prompt("Cluster name"),true,false);
   }

   if(evt.key=="C"){
       game.showCluster(prompt("Cluster name"),false);
   }

   if(evt.key=="N"){
       game.showCluster("noise",false);
   }

   if(evt.key=="+")game.updateScale(1.05,datas);
   if(evt.key=="-")game.updateScale(0.95,datas);

   if(evt.key=="n"){
       game.showCluster("noise",true);
   }

    if(evt.key=="S"){
        //game.clearLinks();
        game.showCluster("",false);
    }

    if(evt.key=="p"){
        game.getVisibleClusters().forEach(c=>{
            var url=location.href.split("offset=")[1];
            game.traceFacets(facets,0,c,Number(url));
        });
    }

    if(evt.key=="o"){
        var url=location.href.split("offset=")[1];
        game.traceFacets(facets_ref,0,null,Number(url));
    }

    if(evt.key=="H"){
        document.getElementById("message").innerHTML="";
    }

    if(evt.key=="h"){
        var text="" +
            "            <br>Commandes sur la visu 3d:<br>\n" +
            "            - <strong>'s'</strong> et SHIFT+'s' respectivement montre et cache toutes les mesures<br>\n" +
            "            - <strong>'m'</strong> et SHIFT+'m' opere un filtre sur les mesures pour les montrer / cacher<br>\n" +
            "            - <strong>'c'</strong> et SHIFT+'c' opere un filtre sur les clusters pour les montrer / cacher<br>\n" +
            "            - <strong>'a'</strong> et SHIFT+'a' engage une autorotation du graphique<br>\n" +
            "            - <strong>'w'</strong> centre la caméra sur l'échantillon pointé par la souris<br>\n" +
            "            - <strong>'v'</strong> et SHIFT+'v' démarre et stop un enregistrement video au format webm (lisible par vlc ou d'autres lecteurs)<br>\n" +
            "            - <strong>'+'</strong> et '-' écarte/réduit les mesure par changement d'échelle <br>\n" +
            "            - <strong>'e'</strong> export les données visibles au format CSV dans le presse papier<br>\n" +
            "            - <strong>'p'</strong> et SHIFT+'p' entoure les clusters visible (patatoides) <br>\n" +
            "            - <strong>'o'</strong> entoure les clusters de référence<br>\n" +
            "            - <strong>'r'</strong> supprime définitivement le bruit (permet d'accéler la navigation)<br>\n" +
            "            - <strong>'k'</strong> connecte entre elles les mesures du même nom<br>\n" +
            "\n" +
            "            - 'click' et 'SHIFT+click' montre / cache le cluster d'appartenance de la mesure<br>\n" +
            "            - 'double click' permet d'étudier un cluster en particulier<br>\n" +
            "            - 'ALT+click' permet grossis / réduit les mesures du même nom<br>\n" +
            "            - 'click droit' permet d'enregistrer la visu en format image";

        document.getElementById("message").innerHTML=text;
        setTimeout(()=>{
            document.getElementById("message").innerHTML="";
        },10000);
    }

    if(evt.key=="P"){
        game.removeFacets();
    }

    if(evt.key=="w"){
        var txt=document.getElementById("row3").innerText;
        if(txt!=null && txt.length>0) {
            var coord = txt.split(",");
            game.setCameraToTarget(coord[0], coord[1], coord[2]);
        }
    }

    if(evt.key=="W"){
        game.setCameraToTarget("0","0","0");
    }

   if(evt.key=="s"){
       game.showCluster("",true);
   }

   if(evt.key=="d"){
       game.clearLinks();
       game.showClosedCluster();
   }

   if(evt.key=="v"){
       game.makeMovie();
   }

   if(evt.key=="V"){
       game.stopMovie();
   }

   if(evt.key=="a") game.startAutoRotation();
   if(evt.key=="A")game.stopAutoRotation();

   if(evt.key=="e"){
       var code=game.toCSV(data_source);
       // @ts-ignore
       navigator.permissions.query({name: "clipboard-write"}).then(result => {
        if (result.state == "granted" || result.state == "prompt") {
            // @ts-ignore
            navigator.clipboard.writeText(code).then(()=>{
                alert("Mesures visible dans le presse-papier au format CSV");
            });
        }else{
            prompt("Copier dans le presse papier",code);
        }
       });
   }


    if(evt.key=="k"){
       game.mesureConnection();
   }

   if(evt.key=="m"){
       game.showMesure(prompt("Measure name"),true);
   }

   if(evt.key=="M"){
       game.showMesure(prompt("Measure name"),false);
   }



   if(evt.key=="r"){
       game.removeNoise();
   }


});