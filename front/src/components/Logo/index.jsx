import logo from '../../img/logo_handix_escuro.png';
import './styles.css';

const Logo = () => {
    
    return (
      <div className="logo-container">
        <img id='logo' src={logo} className='logo' alt='Logo'/>
      </div>
    );
}

export default Logo;