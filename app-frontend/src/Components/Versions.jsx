const Versions = ({modelVersion, appVersion, libVersion}) => {
    return(
        <div class="versions">
            <p>Model Version: {modelVersion}</p>
            <p>App Version: {appVersion}</p>
            <p>Lib Version: {libVersion}</p>
        </div>
    )
} 

export default Versions