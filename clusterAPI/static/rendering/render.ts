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

    private _canvas: HTMLCanvasElement;
    private _engine: BABYLON.Engine;
    private _scene: BABYLON.Scene;
    private _camera: BABYLON.ArcRotateCamera;
    private _light1: BABYLON.Light;
    private _light2: BABYLON.Light;
    private _actionManager:BABYLON.ActionManager;

    constructor(canvasElement : string) {
        // Create canvas and engine.
        this._canvas = document.getElementById(canvasElement) as HTMLCanvasElement;
        this._engine = new BABYLON.Engine(this._canvas, true);
    }


    showCluster(cluster_name,show=true){
        for (let s of this.spheres) {
            var name=s.cluster_name.substr(0,Math.min(cluster_name.length,s.cluster_name.length)).toLowerCase();
            if (name == cluster_name.toLowerCase()){
                if(show)
                    s.material.alpha = _VISIBLE;
                else
                    s.material.alpha = _HIDDEN;
            }
        }
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

                    if(!evt.sourceEvent.altKey)
                        this.showCluster(target.cluster_name,!evt.sourceEvent.shiftKey);
                    else{
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
                    document.getElementById("row3").innerText=
                        "x="+Math.round(target.position.x*1000)/1000+","+
                        "y="+Math.round(target.position.y*1000)/1000+","+
                        "z="+Math.round(target.position.z*1000)/1000;
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
                    for(var i=1;i<4;i++)
                        document.getElementById("row"+i).innerText="";

                }
            )
        );
    }

    createMesure(obj:any,color:BABYLON.Color3,translate:float,expense:float):void {
        var materialSphere = new BABYLON.StandardMaterial("texture2", this._scene);
        materialSphere.diffuseColor = color;
        materialSphere.alpha = 0.9;

        let sphere:any = BABYLON.MeshBuilder.CreateSphere(name,{segments: 16, diameter: 1}, this._scene);

        sphere.position.x = (obj.x+translate)*expense;
        sphere.position.y = (obj.y+translate)*expense;
        sphere.position.z = (obj.z+translate)*expense;
        sphere.material=materialSphere;
        sphere.cluster_name=obj.cluster;
        sphere.name=obj.name;
        sphere.cluster_distance=JSON.parse(obj.cluster_distance);

        this.prepareButton(sphere);
        this.spheres.push(sphere);
    }

    linkSphere(s1:any,s2:any):void {
        let path = [
            new BABYLON.Vector3(s1.position.x, s1.position.y, s1.position.z),
            new BABYLON.Vector3(s2.position.x, s2.position.y, s2.position.z)
        ]

        var tube = BABYLON.MeshBuilder.CreateTube("link"+s1.name+"_"+s2.name, {path: path, radius: 0.04},this._scene);
        this.links.push(tube);
    }

    createScene() : void {
        // Create a basic BJS Scene object.
        this._scene = new BABYLON.Scene(this._engine);
        this._scene.fogMode = BABYLON.Scene.FOGMODE_EXP
        this._scene.fogDensity = 0.002;
        this._scene.fogColor = new BABYLON.Color3(0.9, 0.9, 0.9);
        this._scene.clearColor = new BABYLON.Color4(0.9, 0.9, 0.9);

        this._scene.registerBeforeRender(()=>{

        })

        var dim=_SIZE*2;
        // var scatterPlot = new ScatterPlot([dim,dim,dim],{
        //     x: ["", "0", "1","2"],
        //     y: ["", "0", "1","2"],
        //     z: ["2","1", "0", "-1"]
        // }, this._scene);
        showAxis(50,this._scene);

        // var box = BABYLON.Mesh.CreateBox("box", _SIZE*2, this._scene);
        // var box_material=new BABYLON.StandardMaterial("box_material",this._scene);
        // box_material.alpha=0.1;
        // box_material.diffuseColor = new BABYLON.Color3(0.3, 0.3, 0.3);
        // box.material=box_material;



        // Create a FreeCamera, and set its position to (x:0, y:5, z:-10).
        this._camera = new BABYLON.ArcRotateCamera("Camera", 3*Math.PI / 2, 8*Math.PI/2 , _SIZE*1.5, BABYLON.Vector3.Zero(), this._scene);

        this._actionManager = new BABYLON.ActionManager(this._scene);

        // Target the camera to scene origin.
        this._camera.setTarget(new BABYLON.Vector3(1,1,1));

        // Attach the camera to the canvas.
        this._camera.attachControl(this._canvas, false);

        // Create a basic light, aiming 0,1,0 - meaning, to the sky.
        this._light1 = new BABYLON.HemisphericLight('light1', new BABYLON.Vector3(0,0,-20), this._scene);
        this._light2 = new BABYLON.HemisphericLight('light2', new BABYLON.Vector3(0,0,+20), this._scene);
        this._light1.intensity=0.65;
        this._light2.intensity=0.65;


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

    moveLightToCamera(){

    }

    showClosedCluster() {
        let l=[];
        this.spheres.forEach((s:any)=> {
                if (s.material.alpha == _VISIBLE) {
                    l.push(s);
                }
            });

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

    clearLinks() {
        this.links.forEach((l)=>{
            l.dispose();
        })
        this.links=[];
    }

    removeNoise() {
        this.spheres.forEach((s)=>{
            if(s.cluster_name=="noise")
                s.dispose();
        })
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

/**
 * Affichage des points contenu dans datas
 *
 */
window.addEventListener("message", (evt)=> {
    let datas = evt.data.datas;
    evt.preventDefault();
    if (datas!=null && datas.length>0) {
        game.clearMesures();


        for (let p of datas){
            let color=new BABYLON.Color3(p.style[0],p.style[1],p.style[2]);
            game.createMesure(p,color, 0,_SIZE);
        }



        // game.createMesure("repere","cluster",0,0,0,colors[0],0,_SIZE);
        // game.createMesure("repere","cluster",1,1,1,colors[0],0,_SIZE);
    }
}, false);

window.addEventListener("keypress", (evt)=> {
   if(evt.key=="c"){
       game.showCluster(prompt("Cluster name"),true);
   }

   if(evt.key=="C"){
       game.showCluster(prompt("Cluster name"),false);
   }

   if(evt.key=="N"){
       game.showCluster("noise",false);
   }

   if(evt.key=="n"){
       game.showCluster("noise",true);
   }

    if(evt.key=="h"){
        game.clearLinks();
       game.showCluster("",false);
   }

   if(evt.key=="H"){
       game.showCluster("",true);
   }


   if(evt.key=="d"){
       game.clearLinks();
       game.showClosedCluster();
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